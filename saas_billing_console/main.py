
from utils import add_tenant,add_subscription,record_usage,load_data,calculate_billing,reset_monthly_usage,get_cycle_info

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
            plan = input("Subscription Plan (Free/Premium/Enterprise): ").strip().lower()
            if plan not in ("free", "premium", "enterprise"):
                print("Invalid plan. Use: free, premium, enterprise.")
                continue
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

            try:
                idx = int(input("Choose feature number: "))
                if not (1 <= idx <= len(allowed_features)):
                    raise ValueError
                feature = allowed_features[idx - 1]
            except ValueError:
                 print("Invalid selection.")
                 continue


            try:
               count = int(input("Usage Count: "))
               if count < 0:
                    raise ValueError
            except ValueError:
                print("Invalid count. Must be a non-negative integer.")
                continue

            result = record_usage(tenant_id, feature, count)
            if "error" in result:
                print(f"{result['error']}")
            else:
                billing = calculate_billing(tenant_id)
                print(f"Usage Recorded: {result}")
                print(f"Current Billing: ${billing}")

        elif choice=="4":
            tenant_id=int(input("Tenant ID:"))
            try:
                cycle_start, next_reset = get_cycle_info(tenant_id)
            except ValueError as e:
                print(e)
                continue
            data = load_data()
            sub = next((s for s in data["subscriptions"] if s["tenant_id"] == tenant_id), None)
            plan = sub["plan"]
            usage_list = [u for u in data["usage"] if u["tenant_id"] == tenant_id]

            print(f"\nUsage Summary for Tenant {tenant_id} (plan: {plan})")
            if cycle_start and next_reset:
                print(f"Cycle: {cycle_start.date()} → {next_reset.date()}")

            if not usage_list:
                print("No usage recorded yet.")
            else:           
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