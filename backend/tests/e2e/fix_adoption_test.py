import re

with open('test_adoption_api.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 正則表達式匹配 AdoptionApplication 創建
pattern = r'(application = AdoptionApplication\(\s+)(pet_id=pet\.id,\s+applicant_id=test_adopter_user\.id,\s+status=ApplicationStatus\.PENDING\s+\))'

def replacement(match):
    indent = match.group(1)
    return f'''{indent}application_id=generate_app_id(),
            pet_id=pet.id,
            applicant_id=test_adopter_user.id,
            status=ApplicationStatus.PENDING,
            personal_info={{}},
            living_environment={{}},
            pet_experience={{}}
        )'''

content = re.sub(pattern, replacement, content)

with open('test_adoption_api.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed AdoptionApplication creations")
