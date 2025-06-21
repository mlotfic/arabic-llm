import hydra
from omegaconf import OmegaConf
from schemas.arabic_ner_schema import ArabicNERConfigSchema

@hydra.main(version_base=None, config_path="config", config_name="arabic_ner")
def main(cfg):
    print("YAML Config (raw):")
    print(OmegaConf.to_yaml(cfg))

    # Convert to Pydantic model (validation)
    try:
        ner_config = ArabicNERConfigSchema(**cfg)
        print("\n✅ Pydantic model loaded and validated!")
    except Exception as e:
        print("\n❌ Validation error:", e)
        return

    # Use it like: ner_config.before_honorifics, etc.
    print(f"\nBefore Honorifics: {ner_config.before_honorifics[:3]} ...")

if __name__ == "__main__":
    main()
#     2. Run the script:
#    python main.py 
#