# argos.py

import argostranslate.package
import argostranslate.translate

# --- CONFIGURATION ---
GERMAN_CODE = "de"
ENGLISH_CODE = "en"
DEFAULT_FROM_CODE = GERMAN_CODE 
DEFAULT_TO_CODE = ENGLISH_CODE    

# Global cache to store loaded translation functions
LOADED_MODELS = {} 
SUPPORTED_PAIRS = [
    (GERMAN_CODE, ENGLISH_CODE),
    (ENGLISH_CODE, GERMAN_CODE)
]

def get_translation_key(from_code, to_code):
  """Creates a unique key for the model cache."""
  return f"{from_code}->{to_code}"

def install_package_if_needed(from_code, to_code):
  """Checks for, downloads, and installs a specific Argos package."""
  
  # Check if model is installed using the list of installed packages
  installed_packages = argostranslate.package.get_installed_packages()
  is_installed = any(
    p.from_code == from_code and p.to_code == to_code
    for p in installed_packages
  )

  if not is_installed:
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    
    package_to_install = next(
      (
        p
        for p in available_packages
        if p.from_code == from_code and p.to_code == to_code
      ),
      None,
    )
      
    if package_to_install:
      argostranslate.package.install_from_path(package_to_install.download())
      return True 
    else:
      raise ValueError(f"Translation package for {from_code}->{to_code} is not available in the Argos index.")
  return False

def pre_load_models():
  """
  Called once at server startup to install and load all required models into the cache.
  """
  argostranslate.package.update_package_index()

  for from_code, to_code in SUPPORTED_PAIRS:
    key = get_translation_key(from_code, to_code)
    
    try:
      install_package_if_needed(from_code, to_code)
    except Exception:
      continue 

    try:
      installed_languages = argostranslate.translate.get_installed_languages()
      
      from_lang = next(
        (lang for lang in installed_languages if lang.code == from_code), None
      )
      to_lang = next(
        (lang for lang in installed_languages if lang.code == to_code), None
      )

      if from_lang and to_lang:
        translation_object = from_lang.get_translation(to_lang)
        # FIX APPLIED HERE: Cache the callable method (.translate), not the object
        LOADED_MODELS[key] = translation_object.translate 
    except Exception:
        continue 

# --- EXECUTION: Pre-load the models when the module is imported ---
pre_load_models()


def ensure_model_is_loaded(from_code: str, to_code: str):
  """Checks the cache, loading/installing only as a fallback if pre-load failed."""
  key = get_translation_key(from_code, to_code)

  if key in LOADED_MODELS:
    return LOADED_MODELS[key]

  # FALLBACK (If pre-load failed): Install and load
  try:
    install_package_if_needed(from_code, to_code)
    
    installed_languages = argostranslate.translate.get_installed_languages()
    
    from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
    to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)

    if from_lang and to_lang:
      translation_object = from_lang.get_translation(to_lang)
      # FIX APPLIED HERE: Cache the callable method (.translate), not the object
      LOADED_MODELS[key] = translation_object.translate
      return LOADED_MODELS[key]
    else:
      raise ValueError(f"Required languages ({from_code} or {to_code}) not loaded.")

  except Exception as e:
    return lambda text: f"Error: Model not available for {key}. Details: {e}"


def argos_translate_text(text: str, from_code: str, to_code: str) -> str:
  """The main translation function that uses the dynamic, cached model loader."""
  
  translate_func = ensure_model_is_loaded(from_code, to_code)
  
  try:
    # This execution now correctly calls the cached .translate method
    translated_text = translate_func(text) 
    return translated_text
      
  except Exception as e:
    return f"Translation failed: {e}"