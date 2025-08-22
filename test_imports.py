#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
Run with: python savemax/test_imports.py
"""

def test_imports():
    """Test all module imports."""
    try:
        print("Testing imports...")
        
        # Test app package imports
        from savemax.app.auth import is_authenticated, login, logout, signup, SESSION_USER_KEY
        print("✓ auth module imported successfully")
        
        from savemax.app.calculator import TaxInputs, calculate_old_regime, calculate_new_regime
        print("✓ calculator module imported successfully")
        
        from savemax.app.database import ensure_dbs, save_history, get_recent_history
        print("✓ database module imported successfully")
        
        from savemax.app.recommender import compare_regimes, generate_suggestions
        print("✓ recommender module imported successfully")
        
        from savemax.app.ui_components import gradient_header, metric_card, two_column_metrics, format_inr
        print("✓ ui_components module imported successfully")
        
        from savemax.app.exports import export_csv, export_pdf
        print("✓ exports module imported successfully")
        
        print("\n🎉 All imports successful! The package structure is correct.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports() 