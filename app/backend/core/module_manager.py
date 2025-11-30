from typing import Dict, Any, Optional
from backend.core.base_module import BaseModule


class ModuleManager:
    """モジュール管理システム - モジュール間通信の仲介役"""
    
    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}
    
    def register_module(self, module: BaseModule) -> bool:
        """モジュールを登録"""
        if module.name in self._modules:
            raise ValueError(f"Module '{module.name}' is already registered")
        
        self._modules[module.name] = module
        return module.initialize()
    
    def unregister_module(self, module_name: str) -> bool:
        """モジュールの登録を解除"""
        if module_name in self._modules:
            del self._modules[module_name]
            return True
        return False
    
    def get_module(self, module_name: str) -> Optional[BaseModule]:
        """モジュールを取得"""
        return self._modules.get(module_name)
    
    def call_module(
        self, 
        module_name: str, 
        action: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """モジュールのアクションを呼び出す（モジュール間通信の仲介）"""
        module = self.get_module(module_name)
        
        if not module:
            raise ValueError(f"Module '{module_name}' not found")
        
        if not module.is_enabled():
            raise RuntimeError(f"Module '{module_name}' is disabled")
        
        return module.execute(action, params)
    
    def list_modules(self) -> Dict[str, Dict[str, Any]]:
        """登録されているすべてのモジュール情報を取得"""
        return {
            name: module.get_info() 
            for name, module in self._modules.items()
        }
    
    def enable_module(self, module_name: str) -> bool:
        """モジュールを有効化"""
        module = self.get_module(module_name)
        if module:
            module.enable()
            return True
        return False
    
    def disable_module(self, module_name: str) -> bool:
        """モジュールを無効化"""
        module = self.get_module(module_name)
        if module:
            module.disable()
            return True
        return False


# グローバルなモジュールマネージャーインスタンス
module_manager = ModuleManager()
