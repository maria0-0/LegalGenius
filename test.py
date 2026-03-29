import sys
import logging
from legal_crew import auditeaza_contract_complet

# Turn on debug logging to see what CrewAI is actually doing
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    test_text = "Contract de muncă. Salariul este 2000 RON. Angajatul trebuie să muncească 14 ore pe zi. Nu primește concediu."
    print("Testing audit tool...")
    
    try:
        result = auditeaza_contract_complet(test_text)
        print("RESULT:")
        print(result)
    except Exception as e:
        print("ERROR:", e)
