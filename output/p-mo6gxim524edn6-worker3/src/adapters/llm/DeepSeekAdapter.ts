import { BaseLLMAdapter } from './BaseLLMAdapter';
import {
  LLMConfig,
  LLMMessage,
  LLMRequestOptions,
  LLMResponse,
  LLMStreamChunk,
  LLMBaseError
} from './interfaces/ILLMAdapter';
import { Logger } from '../../utils/logger';

/**
 * DeepSeek V4模型常量
 */
export const DEEPSEEK_V4_MODELS = {
  /** V4 Flash - 快速响应，适合高并发 */
  V4_FLASH: 'deepseek-v4-flash',
  /** V4 Pro - 深度推理，适合复杂任务 */
  V4_PRO: 'deepseek-v4-pro',
  /** DeepSeek Chat */
  CHAT: 'deepseek-chat',
  /** DeepSeek Coder */
  CODER: 'deepseek-coder',
} as const;

/**
 * DeepSeek API响应扩展（包含推理内容）
 * 不再继承 APIResponse，避免 choices 类型不兼容
 */
interface DeepSeekAPIResponse {
  id?: string;
  object?: string;
  created?: number;
  model: string;
  choices: Array<{
    index: number;
    message?: {
      role: string;
      content: string;
      reasoning_content?: string;
    };
    delta?: {
      role?: string;
      content?: string;
      reasoning_content?: string;
    };
    finish_reason?: string;
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    completion_tokens_details?: {
      reasoning_tokens: number;
    };
  };
  error?: {
    message: string;
    type?: string;
    code?: string;
  };
}

/**
 * DeepSeek适配器
 * 
 * 支持：
 * - DeepSeek V4 Flash: 快速响应，适合高并发场景
 * - DeepSeek V4 Pro: 深度推理，适合复杂任务
 * - 原生推理能力（reasoning_content）
 * 
 * 成本优势：比GPT-4便宜100倍+
 */
export class DeepSeekAdapter extends BaseLLMAdapter {
  public readonly provider = 'deepseek';
  protected readonly logger: Logger;

  constructor(config?: LLMConfig) {
    super(config);
    this.logger = new Logger('DeepSeekAdapter');
  }

  initialize(config: LLMConfig): void {
    const mergedConfig: LLMConfig = {
      baseUrl: 'https://api.deepseek.com/v1',
      costPer1kPrompt: 0.001,  // ¥1/百万tokens
      costPer1kCompletion: 0.002, // ¥2/百万tokens
      ...config,
      // 确保 model 有默认值（如果 config 中未提供）
      model: config.model || DEEPSEEK_V4_MODELS.V4_PRO,
    };
    super.initialize(mergedConfig);
    this.logger.info('DeepSeek适配器初始化完成', { 
      model: mergedConfig.model,
      baseUrl: mergedConfig.baseUrl 
    });
  }

  async createChatCompletion(
    messages: LLMMessage[],
    options?: Partial<LLMRequestOptions>
  ): Promise<LLMResponse> {
    this.ensureReady();
    const startTime = Date.now();

    return this.fetchWithRetry(async () => {
      const url = `${this._config.baseUrl}/chat/completions`;
      const body = this.buildRequestBody(messages, { ...options, stream: false });

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this._config.apiKey}`
        },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(options?.timeoutMs ?? this._config.timeoutMs ?? 60000)
      });

      const data = await response.json() as DeepSeekAPIResponse;

      if (!response.ok) {
        this.handleApiError(response, data);
      }

      const result = this.parseDeepSeekResponse(data, startTime);
      this.accumulateUsage(result.usage.promptTokens, result.usage.completionTokens);
      return result;
    });
  }

  async* createChatCompletionStream(
    messages: LLMMessage[],
    options?: Partial<LLMRequestOptions>
  ): AsyncGenerator<LLMStreamChunk, void, unknown> {
    this.ensureReady();
    const startTime = Date.now();

    const url = `${this._config.baseUrl}/chat/completions`;
    const body = this.buildRequestBody(messages, { ...options, stream: true });

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this._config.apiKey}`
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(options?.timeoutMs ?? this._config.timeoutMs ?? 60000)
    });

    if (!response.ok) {
      const error = await response.json();
      this.handleApiError(response, error);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new LLMBaseError('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed === '' || trimmed === 'data: [DONE]') continue;
          if (!trimmed.startsWith('data: ')) continue;

          try {
            const json = JSON.parse(trimmed.slice(6));
            const chunk = this.parseStreamChunk(json, startTime);
            if (chunk) yield chunk;
          } catch (e) {
            this.logger.warn('Failed to parse stream chunk', { line: trimmed });
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * 确保适配器已初始化
   */
  protected ensureReady(): void {
    if (!this.isReady()) {
      throw new LLMBaseError('DeepSeekAdapter not initialized. Call initialize() first.');
    }
  }

  /**
   * 构建请求体
   */
  protected buildRequestBody(
    messages: LLMMessage[],
    options?: Partial<LLMRequestOptions>
  ): Record<string, unknown> {
    return {
      model: options?.model ?? this._config.model,
      messages,
      temperature: options?.temperature,
      max_tokens: options?.maxTokens,
      top_p: options?.topP,
      stop: options?.stop,
      stream: options?.stream ?? false,
      frequency_penalty: options?.frequencyPenalty,
      presence_penalty: options?.presencePenalty,
    };
  }

  /**
   * 解析DeepSeek响应（包含推理内容）
   */
  private parseDeepSeekResponse(data: DeepSeekAPIResponse, startTime: number): LLMResponse {
    const choice = data.choices?.[0];
    if (!choice) {
      throw new LLMBaseError('No choices in response');
    }

    const usage = data.usage || {
      prompt_tokens: 0,
      completion_tokens: 0,
      total_tokens: 0
    };

    const reasoningTokens = usage.completion_tokens_details?.reasoning_tokens || 0;
    const content = choice.message?.content || '';

    return {
      content,
      model: data.model || this._config.model,
      finishReason: this.mapFinishReason(choice.finish_reason || 'stop'),
      usage: {
        promptTokens: usage.prompt_tokens,
        completionTokens: usage.completion_tokens,
        totalTokens: usage.total_tokens,
        reasoningTokens
      },
      latencyMs: Date.now() - startTime,
      id: data.id || `deepseek-${Date.now()}`,
      message: choice.message ? {
        role: choice.message.role,
        content: choice.message.content,
        reasoningContent: choice.message.reasoning_content
      } : undefined,
      created: data.created || Math.floor(Date.now() / 1000),
      rawResponse: data
    };
  }

  /**
   * 解析流式chunk
   */
  private parseStreamChunk(data: any, startTime: number): LLMStreamChunk | null {
    const choice = data.choices?.[0];
    if (!choice) return null;

    const content = choice.delta?.content || '';
    const finishReason = choice.finish_reason ? this.mapFinishReason(choice.finish_reason) : undefined;

    return {
      content,
      finishReason,
      isFirst: false, // 流式 chunk 的 isFirst 由调用方判断
      isLast: finishReason === 'stop',
      id: data.id,
      delta: {
        role: choice.delta?.role,
        content: choice.delta?.content || '',
        reasoningContent: choice.delta?.reasoning_content
      }
    };
  }

  /**
   * 映射完成原因
   */
  private mapFinishReason(reason: string): 'stop' | 'length' | 'content_filter' | 'tool_calls' {
    const mapping: Record<string, 'stop' | 'length' | 'content_filter' | 'tool_calls'> = {
      'stop': 'stop',
      'length': 'length',
      'content_filter': 'content_filter',
      'tool_calls': 'tool_calls'
    };
    return mapping[reason] || 'stop';
  }

  /**
   * 获取可用模型列表
   */
  async listModels(): Promise<Array<{ id: string; name: string }>> {
    return [
      { id: DEEPSEEK_V4_MODELS.V4_FLASH, name: 'DeepSeek V4 Flash (快速响应)' },
      { id: DEEPSEEK_V4_MODELS.V4_PRO, name: 'DeepSeek V4 Pro (深度推理)' },
      { id: DEEPSEEK_V4_MODELS.CHAT, name: 'DeepSeek Chat' },
      { id: DEEPSEEK_V4_MODELS.CODER, name: 'DeepSeek Coder' }
    ];
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this._config.baseUrl}/models`, {
        headers: {
          'Authorization': `Bearer ${this._config.apiKey}`
        }
      });
      return response.ok;
    } catch (error) {
      this.logger.error('Health check failed', { error });
      return false;
    }
  }
}
