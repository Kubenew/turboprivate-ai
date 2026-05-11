"""Example: Quantize a HuggingFace model via the CLI."""
# CLI equivalent:
#   turbo model quantize meta-llama/Llama-3.1-8B --bits 4 --method awq

import asyncio

from turbo.inference.quantize import QuantConfig, Quantizer


async def main():
    quantizer = Quantizer(method="awq", bits=4)
    config = QuantConfig(group_size=32, activation_aware=True)

    # Quantize a local model
    result = await quantizer.quantize(
        model_name="meta-llama/Llama-3.1-8B",
        output_path="./models/llama3-8b-int4",
        config=config,
    )
    print(f"Quantized model saved to: {result}")


if __name__ == "__main__":
    asyncio.run(main())
