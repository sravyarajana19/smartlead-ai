from backend.core.config import RANDOM_SEED
from generator.synthetic_data import SyntheticDataGenerator


def test_generator_deterministic_output():
    gen1 = SyntheticDataGenerator(seed=RANDOM_SEED, scale="small")
    data1 = gen1.generate_all()

    gen2 = SyntheticDataGenerator(seed=RANDOM_SEED, scale="small")
    data2 = gen2.generate_all()

    assert len(data1["leads"]) == len(data2["leads"])
    assert len(data1["companies"]) == len(data2["companies"])
    assert len(data1["opportunities"]) == len(data2["opportunities"])

    # Verify first and last IDs match
    assert data1["leads"][0]["id"] == data2["leads"][0]["id"]
    assert data1["leads"][-1]["id"] == data2["leads"][-1]["id"]
    assert data1["leads"][0]["lead_score"] == data2["leads"][0]["lead_score"]
