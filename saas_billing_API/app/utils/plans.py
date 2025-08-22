plans = {
    "free": {
        "price": 0,
        "features": ["api_calls"],
        "quotas": {
            "api_calls": 100
        },
        "pricing": {
            "api_calls": 0.1
        }
    },
    "premium": {
        "price": 50,
        "features": ["api_calls", "storage"],
        "quotas": {
            "api_calls": 1000,
            "storage": 500
        },
        "pricing": {
            "api_calls": 0.1,
            "storage": 0.5
        }
    },
    "enterprise": {
        "price": 100,
        "features": ["api_calls", "storage"],
        "quotas": {
            "api_calls": None,
            "storage": None
        },
        "pricing": {}
    }
}
