
from utils import add_tenant,add_subscription,record_usage,load_data,calculate_billing

def main():
    while True:
        print("\n--- SaaS Billing Console ---")
        print("1. Add Tenant")
        print("2. Add Subscription")
        print("3. Record Usage")
        print("4. Exit")


        
        choice = input("Choose an option: ")

        if choice == "1":
            name = input("Tenant Name: ")
            tenant = add_tenant(name)
            print(f"Tenant Added: {tenant}")

        elif choice == "2":
            tenant_id = int(input("Tenant ID: "))
            plan = input("Subscription Plan (Free/Premium/Enterprise): ")
            subscription = add_subscription(tenant_id, plan)
            print(f"Subscription Added: {subscription}")

      
        elif choice == "3":
            tenant_id = int(input("Tenant ID: "))
            data = load_data()

            subscription = next((s for s in data["subscriptions"] if s["tenant_id"] == tenant_id), None)
            if not subscription:
                print(f"Tenant {tenant_id} has no active subscription.")
                continue

            plan = subscription["plan"]
            allowed_features = data["plans"].get(plan, [])

            print(f"\nTenant {tenant_id} is on '{plan}' plan.")
            print("Allowed Features:")
            for i, feat in enumerate(allowed_features, start=1):
                print(f" {i}. {feat}")

            feature = input("Enter Feature Used: ")
            count = int(input("Usage Count: "))

            result = record_usage(tenant_id, feature, count)
            if "error" in result:
                print(f"{result['error']}")
            else:
                billing = calculate_billing(tenant_id)
                print(f"Usage Recorded: {result}")
                print(f"Current Billing: ${billing}")
        
        elif choice == "4":
            print("Exiting")
            break    
 

        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()