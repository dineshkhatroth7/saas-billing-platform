
from utils import add_tenant,add_subscription,record_usage,load_data,calculate_billing,reset_monthly_usage

def main():
    while True:
        print("\n--- SaaS Billing Console ---")
        print("1. Add Tenant")
        print("2. Add Subscription")
        print("3. Record Usage")
        print("4. View Usage Summary")
        print("5. Run Monthly Reset")
        print("6. Exit")


        
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

        elif choice=="4":
            tenant_id=int(input("Tenant ID:"))
            data = load_data()
            usage_list = [u for u in data["usage"] if u["tenant_id"] == tenant_id]
            if not usage_list:
                print("No usage recorded yet.")
            else:
                print(f"\nUsage Summary for Tenant {tenant_id}:")
                for u in usage_list:
                    print(f"- {u['feature']}: {u['count']} times on {u['timestamp']}")
                billing = calculate_billing(tenant_id)
                print(f" Total Billing: ${billing}")

         
        elif choice == "5":
            tenants_reset = reset_monthly_usage()
            if tenants_reset:   
                print("Monthly usage reset for tenants:")
            for t in tenants_reset:
                print(f"- ID: {t['id']} | Name: {t['name']}")
                print(f"  New Cycle Start: {t['new_cycle_start']}")
            else:   
                print("No tenants due for reset.")


        elif choice == "6":
            print("Exiting")
            break    
 

        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()