from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseModule(ABC):
    """すべての機能モジュールの基底クラス"""
    
    def __init__(self, name: str):
        self.name = name
        self._enabled = True
    
    @abstractmethod
    def initialize(self) -> bool:
        """モジュールの初期化処理"""
        pass
    
    @abstractmethod
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """モジュールのアクション実行"""
        pass
    
    def enable(self):
        """モジュールを有効化"""
        self._enabled = True
    
    def disable(self):
        """モジュールを無効化"""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """モジュールが有効かどうかを確認"""
        return self._enabled
    
    def get_info(self) -> Dict[str, Any]:
        """モジュール情報を取得"""
        return {
            "name": self.name,
            "enabled": self._enabled
        }
