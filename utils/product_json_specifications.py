# JSON SPECIFICATIONS 
skincare_specifications_schema = {
    "type": "object",
    "properties": {
        "skinType": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["Normal", "Dry", "Oily", "Combination", "Sensitive"]
            },
            "minItems": 1
        },
        "ingredients": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "minItems": 1
        },
        "purpose": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["Hydration", "Anti-aging", "Brightening", "Sun protection", "Deep cleansing"]
            },
            "minItems": 1
        },
        "texture": {
            "type": "string",
            "enum": ["Gel", "Cream", "Foam", "Oil"]
        },
        "volume": {
            "type": "string",
            "pattern": "^[0-9]+(ml|ML|oz|OZ)$" 
        }
    },
    "required": ["skinType", "ingredients", "purpose", "texture", "volume"]
}

makeup_schema = {
    "type": "object",
    "properties": {
        "shade": {"type": "string", "minLength": 1},
        "finish": {"type": "string", "enum": ["Matte", "Satin", "Glossy", "Dewy"]},
        "coverage": {"type": "string", "enum": ["Light", "Medium", "Full"]},
        "waterproof": {"type": "boolean"},
        "ingredients": {
            "type": "array",
            "items": {"type": "string", "enum": ["Paraben-free", "Cruelty-free", "Vegan"]},
            "minItems": 1
        },
        "volumeWeight": {"type": "string", "pattern": "^[0-9]+(ml|g|oz)$"}
    },
    "required": ["shade", "finish", "coverage", "waterproof", "ingredients", "volumeWeight"]
}

haircare_schema = {
    "type": "object",
    "properties": {
        "hairType": {
            "type": "array",
            "items": {"type": "string", "enum": ["Straight", "Wavy", "Curly", "Coily", "Colored"]},
            "minItems": 1
        },
        "purpose": {
            "type": "array",
            "items": {"type": "string", "enum": ["Repair", "Hydration", "Volume", "Anti-dandruff", "Color protection"]},
            "minItems": 1
        },
        "ingredients": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "volume": {"type": "string", "pattern": "^[0-9]+(ml|L|oz)$"},
        "tools": {"type": "string"}
    },
    "required": ["hairType", "purpose", "ingredients", "volume"]
}

fragrances_schema = {
    "type": "object",
    "properties": {
        "fragranceFamily": {"type": "string", "enum": ["Floral", "Woody", "Citrus", "Fresh", "Oriental"]},
        "concentration": {"type": "string", "enum": ["Eau de Parfum (EDP)", "Eau de Toilette (EDT)", "Eau de Cologne (EDC)"]},
        "notes": {
            "type": "object",
            "properties": {
                "top": {"type": "string"},
                "middle": {"type": "string"},
                "base": {"type": "string"}
            },
            "required": ["top", "middle", "base"]
        },
        "volume": {"type": "string", "pattern": "^[0-9]+(ml|oz)$"}
    },
    "required": ["fragranceFamily", "concentration", "notes", "volume"]
}

bodycare_schema = {
    "type": "object",
    "properties": {
        "skinBenefits": {
            "type": "array",
            "items": {"type": "string", "enum": ["Hydrating", "Exfoliating", "Soothing"]},
            "minItems": 1
        },
        "ingredients": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "texture": {"type": "string", "enum": ["Cream", "Gel", "Scrub"]},
        "volume": {"type": "string", "pattern": "^[0-9]+(ml|oz)$"}
    },
    "required": ["skinBenefits", "ingredients", "texture", "volume"]
}

nailcare_schema = {
    "type": "object",
    "properties": {
        "nailPolish": {
            "type": "object",
            "properties": {
                "finish": {"type": "string", "enum": ["Glossy", "Matte"]},
                "color": {"type": "string"}
            },
            "required": ["finish", "color"]
        },
        "ingredients": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "nailTools": {"type": "string"},
        "treatments": {"type": "array", "items": {"type": "string"}, "minItems": 1}
    },
    "required": ["nailPolish", "ingredients"]
}

mens_grooming_schema = {
    "type": "object",
    "properties": {
        "skinType": {
            "type": "array",
            "items": {"type": "string", "enum": ["Normal", "Oily", "Sensitive"]},
            "minItems": 1
        },
        "ingredients": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "purpose": {
            "type": "array",
            "items": {"type": "string", "enum": ["Hydration", "Soothing post-shave", "Fragrance"]},
            "minItems": 1
        },
        "volume": {"type": "string", "pattern": "^[0-9]+(ml|oz)$"}
    },
    "required": ["skinType", "ingredients", "purpose", "volume"]
}

tools_accessories_schema = {
    "type": "object",
    "properties": {
        "material": {"type": "string", "enum": ["Synthetic", "Natural Bristles"]},
        "heatSettings": {"type": "integer", "minimum": 1, "maximum": 10}, 
        "size": {"type": "string", "enum": ["Compact", "Full-size"]},
        "powerWattage": {
            "type": "string",
            "pattern": "^(?:[0-9]+W|N/A)$"
        }
    },
    "required": ["material", "heatSettings", "size", "powerWattage"]
}

natural_organic_schema = {
    "type": "object",
    "properties": {
        "ingredients": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "description": "Must be 100% organic and plant-based"
        },
        "certifications": {
            "type": "array",
            "items": {"type": "string", "enum": ["USDA Organic", "Cruelty-Free"]},
            "minItems": 1
        },
        "packaging": {"type": "string", "enum": ["Recyclable", "Biodegradable"]}
    },
    "required": ["ingredients", "certifications", "packaging"]
}

beauty_supplements_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["Capsules", "Powders", "Gummies"]},
        "keyNutrients": {
            "type": "array",
            "items": {"type": "string", "enum": ["Biotin", "Collagen", "Vitamin E", "Zinc"]},
            "minItems": 1
        },
        "purpose": {
            "type": "array",
            "items": {"type": "string", "enum": ["Strengthen hair", "Improve skin elasticity", "Nail health"]},
            "minItems": 1
        },
        "servingSize": {"type": "string", "pattern": "^[0-9]+-day supply$"}  
    },
    "required": ["type", "keyNutrients", "purpose", "servingSize"]
}