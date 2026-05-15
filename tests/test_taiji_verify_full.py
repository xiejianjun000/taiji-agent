"""
Taiji Verify 完整单元测试

覆盖模块:
- kun_guard: 坤守 - 语义残差修正
- qian_advance: 乾进 - 语义演进建模  
- fu_return: 复归 - 崩溃逆转
- guan_observe: 观变 - 状态追踪
- polaris: 北辰编译器
- symptom_map: 病候图
"""

import numpy as np
import pytest


class TestKunGuard:
    """坤守模块测试"""
    
    def test_kun_guard_init(self):
        from taiji_agent.taiji_verify.kun_guard import KunGuard
        guard = KunGuard(correction_factor=0.5)
        assert guard.m == 0.5
    
    def test_compute_residual(self):
        from taiji_agent.taiji_verify.kun_guard import KunGuard
        guard = KunGuard()
        input_vec = np.array([1.0, 0.0, 0.0])
        ground_vec = np.array([0.0, 1.0, 0.0])
        residual = guard.compute_residual(input_vec, ground_vec)
        assert 0 <= residual <= 1.0
    
    def test_check_hazard(self):
        from taiji_agent.taiji_verify.kun_guard import KunGuard, HazardLevel
        guard = KunGuard()
        
        level, needs_correction = guard.check_hazard(0.2)
        assert level == HazardLevel.LOW
        assert not needs_correction
        
        level, needs_correction = guard.check_hazard(0.7)
        assert level == HazardLevel.HIGH
        assert needs_correction
    
    def test_correct(self):
        from taiji_agent.taiji_verify.kun_guard import KunGuard, HazardLevel
        guard = KunGuard()
        input_vec = np.array([1.0, 0.5, 0.2])
        ground_vec = np.array([0.9, 0.4, 0.3])
        
        result = guard.correct(input_vec, ground_vec)
        assert result.corrected_vector is not None
        assert 0 <= result.residual <= 1.0
    
    def test_add_knowledge_anchor(self):
        from taiji_agent.taiji_verify.kun_guard import KunGuard
        guard = KunGuard()
        vec = np.array([1.0, 0.0, 0.0])
        anchor_id = guard.add_knowledge_anchor("测试锚点", vec)
        assert anchor_id is not None
        assert guard.anchors_count == 1
    
    def test_correct_with_projection(self):
        from taiji_agent.taiji_verify.kun_guard import KunGuard, HazardLevel
        guard = KunGuard()
        guard.add_knowledge_anchor("锚点", np.array([1.0, 0.0, 0.0]))
        
        # 使用差异较大的向量来触发修正
        input_vec = np.array([1.0, 0.0, 0.0])
        ground_vec = np.array([0.0, 1.0, 0.0])
        
        result = guard.correct_with_projection(input_vec, ground_vec)
        assert result.corrected_vector is not None


class TestQianAdvance:
    """乾进模块测试"""
    
    def test_qian_advance_init(self):
        from taiji_agent.taiji_verify.qian_advance import QianAdvance
        advance = QianAdvance(k_paths=5, noise_scale=0.1)
        assert advance.k_paths == 5
    
    def test_perturb(self):
        from taiji_agent.taiji_verify.qian_advance import QianAdvance
        advance = QianAdvance(k_paths=3)
        vec = np.array([1.0, 0.0, 0.0])
        
        results = advance.perturb(vec)
        assert len(results) == 3
        for r in results:
            assert r.similarity >= 0.0
    
    def test_compute_stability(self):
        from taiji_agent.taiji_verify.qian_advance import QianAdvance, PerturbationResult
        advance = QianAdvance()
        
        results = [
            PerturbationResult(path_id=0, perturbed_vector=np.array([1.0, 0.0]), distance_change=0.1, similarity=0.9),
            PerturbationResult(path_id=1, perturbed_vector=np.array([0.9, 0.1]), distance_change=0.05, similarity=0.95),
        ]
        
        stability = advance.compute_stability(results)
        assert 0 <= stability <= 1.0
    
    def test_evolve(self):
        from taiji_agent.taiji_verify.qian_advance import QianAdvance
        advance = QianAdvance(max_iterations=2)
        vec = np.random.rand(3)
        
        result = advance.evolve(vec)
        assert result.stability_score >= 0.0
        assert result.converged is not None
    
    def test_analyze_paths(self):
        from taiji_agent.taiji_verify.qian_advance import QianAdvance
        advance = QianAdvance()
        vec = np.array([1.0, 0.5, 0.2])
        
        avg_delta, avg_sim, stability = advance.analyze_paths(vec)
        assert 0 <= avg_delta <= 1.0
        assert 0 <= avg_sim <= 1.0
        assert 0 <= stability <= 1.0


class TestFuReturn:
    """复归模块测试"""
    
    def test_fu_return_init(self):
        from taiji_agent.taiji_verify.fu_return import FuReturn
        fu_return = FuReturn(Bc=0.8, eps=0.01)
        assert fu_return.Bc == 0.8
    
    def test_compute_lyapunov(self):
        from taiji_agent.taiji_verify.fu_return import FuReturn
        fu_return = FuReturn()
        
        history = [
            np.array([1.0, 0.0, 0.0]),
            np.array([1.1, 0.1, 0.0]),
            np.array([1.2, 0.2, 0.1]),
        ]
        
        lyapunov = fu_return.compute_lyapunov_exponent(history)
        assert isinstance(lyapunov, float)
    
    def test_detect_crash(self):
        from taiji_agent.taiji_verify.fu_return import FuReturn, RecoveryState
        fu_return = FuReturn()
        
        state = fu_return.detect_crash(1.0, 0.95)
        assert state == RecoveryState.CRASHING
        
        state = fu_return.detect_crash(0.3, 0.2)
        assert state == RecoveryState.NORMAL
    
    def test_recover(self):
        from taiji_agent.taiji_verify.fu_return import FuReturn
        fu_return = FuReturn(max_retries=5, eps=0.5)  # 放宽收敛阈值
        
        current_vec = np.array([1.0, 0.0, 0.0])
        stable_vec = np.array([0.5, 0.5, 0.0])
        
        result = fu_return.recover(current_vec, stable_vec)
        assert result.final_state is not None
    
    def test_adaptive_recover(self):
        from taiji_agent.taiji_verify.fu_return import FuReturn
        fu_return = FuReturn(eps=0.5)  # 放宽收敛阈值
        
        current_vec = np.array([1.0, 0.0, 0.0])
        stable_vec = np.array([0.5, 0.5, 0.0])
        
        result = fu_return.adaptive_recover(current_vec, stable_vec, lyapunov=0.6)
        assert result.final_state is not None


class TestGuanObserve:
    """观变模块测试"""
    
    def test_guan_observe_init(self):
        from taiji_agent.taiji_verify.guan_observe import GuanObserve
        observer = GuanObserve(window_size=10)
        assert observer.window_size == 10
    
    def test_track(self):
        from taiji_agent.taiji_verify.guan_observe import GuanObserve
        observer = GuanObserve()
        vec = np.array([1.0, 0.0, 0.0])
        
        snapshot = observer.track(vec)
        assert snapshot is not None
        assert observer.history_length == 1
    
    def test_analyze_trend(self):
        from taiji_agent.taiji_verify.guan_observe import GuanObserve
        observer = GuanObserve(window_size=5)
        
        for _ in range(5):
            observer.track(np.random.rand(3))
        
        trend = observer.analyze_trend()
        assert trend.change_type is not None
    
    def test_detect_anomalies(self):
        from taiji_agent.taiji_verify.guan_observe import GuanObserve, ChangeType
        observer = GuanObserve(similarity_threshold=0.9)
        
        observer.set_reference(np.array([1.0, 0.0, 0.0]))
        observer.track(np.array([1.0, 0.0, 0.0]))  # 第一次跟踪（稳定）
        snapshot = observer.track(np.array([0.1, 0.9, 0.0]))  # 第二次跟踪（低相似度，应触发异常）
        
        # 检查是否检测到异常类型
        assert snapshot.change_type == ChangeType.ANOMALY


class TestPolarisCompiler:
    """北辰编译器测试"""
    
    def test_polaris_init(self):
        from taiji_agent.taiji_verify.polaris import PolarisCompiler
        compiler = PolarisCompiler(max_rounds=10)
        assert compiler.max_rounds == 10
    
    def test_compile(self):
        from taiji_agent.taiji_verify.polaris import PolarisCompiler
        compiler = PolarisCompiler()
        
        result = compiler.compile("分析文档")
        assert result.success is True
        assert len(result.atom_table) > 0
    
    def test_execute(self):
        from taiji_agent.taiji_verify.polaris import PolarisCompiler
        
        def executor(atom):
            return f"完成: {atom.description}"
        
        compiler = PolarisCompiler()
        compiler.compile("生成报告")
        
        result = compiler.execute(executor)
        assert result.success is True
    
    def test_task_atom_methods(self):
        from taiji_agent.taiji_verify.polaris import TaskAtom, TaskState
        
        atom = TaskAtom(atom_id="test", type="atomic", description="测试")
        assert atom.is_ready() is True
        
        atom.activate()
        assert atom.state == TaskState.ACTIVE
        
        atom.complete("done")
        assert atom.state == TaskState.COMPLETED


class TestSymptomMap:
    """病候图测试"""
    
    def test_symptom_map_init(self):
        from taiji_agent.taiji_verify.symptom_map import SymptomMap
        symptom_map = SymptomMap()
        # 18种检测器（4个RAG + 4个Reasoning + 3个Memory + 3个Agent + 2个Tool + 1个Safety + 1个Knowledge + 1个Knowledge）
        assert len(symptom_map.get_detectors()) == 18
    
    def test_detect(self):
        from taiji_agent.taiji_verify.symptom_map import SymptomMap
        symptom_map = SymptomMap()
        
        result = symptom_map.detect("正常文本")
        assert result.passed is True
    
    def test_detect_by_level(self):
        from taiji_agent.taiji_verify.symptom_map import SymptomMap, FailureLevel
        symptom_map = SymptomMap()
        
        failures = symptom_map.detect_by_level("测试文本", FailureLevel.RAG)
        assert isinstance(failures, list)
    
    def test_rag_retrieval_failure_detector(self):
        from taiji_agent.taiji_verify.symptom_map import RAGRetrievalFailureDetector
        detector = RAGRetrievalFailureDetector()
        
        result = detector.detect("", {"retrieved_docs": []})
        assert result is not None
        assert result.pattern.value == "rag_retrieval_failure"
    
    def test_reasoning_hallucination_detector(self):
        from taiji_agent.taiji_verify.symptom_map import ReasoningHallucinationDetector
        detector = ReasoningHallucinationDetector()
        
        result = detector.detect("根据内部知识，研究表明这是正确的")
        assert result is not None
    
    def test_add_remove_detector(self):
        from taiji_agent.taiji_verify.symptom_map import SymptomMap, FailurePattern
        symptom_map = SymptomMap()
        
        original_count = len(symptom_map.get_detectors())
        symptom_map.remove_detector(FailurePattern.RAG_RETRIEVAL_FAILURE)
        assert len(symptom_map.get_detectors()) == original_count - 1


class TestDeltaS:
    """阴阳距测试"""
    
    def test_delta_s_init(self):
        from taiji_agent.taiji_verify.delta_s import DeltaSCalculator
        calculator = DeltaSCalculator()
        assert calculator._thresholds['safe'] == 0.4
    
    def test_compute(self):
        from taiji_agent.taiji_verify.delta_s import DeltaSCalculator, GateZone
        calculator = DeltaSCalculator()
        
        input_vec = np.array([1.0, 0.0, 0.0])
        ground_vec = np.array([0.9, 0.1, 0.0])
        
        result = calculator.compute(input_vec, ground_vec)
        assert result.delta_s >= 0.0
        assert result.zone is not None
        assert isinstance(result.zone, GateZone)


class TestXunTune:
    """巽调测试"""
    
    def test_xun_tune_init(self):
        from taiji_agent.taiji_verify.xun_tune import XunTune
        xun_tune = XunTune(gamma=0.618)
        assert xun_tune.gamma == 0.618
    
    def test_modulate(self):
        from taiji_agent.taiji_verify.xun_tune import XunTune
        xun_tune = XunTune()
        
        output_vectors = [np.random.rand(5) for _ in range(3)]
        attention_weights = np.random.rand(3)
        
        result = xun_tune.modulate(output_vectors, attention_weights)
        assert result.content_vector is not None
        assert result.modulation_factor > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
