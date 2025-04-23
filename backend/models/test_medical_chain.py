# test_medical_chain.py
import pytest
from models.medical_chain import get_response

def test_get_response():
    question = "What are the symptoms of allergies?"
    answer = get_response(question)
    assert isinstance(answer, str), "The response should be a string."
    # You can add more assertions based on expected keywords
    assert "allergy" in answer.lower(), "The answer should mention allergies."

if __name__ == "__main__":
    pytest.main()
