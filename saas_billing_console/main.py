
from utils import add_tenant,add_subscription

def main():
    while True:
        print("\n--- SaaS Billing Console ---")
        print("1. Add Tenant")
        print("2. Add Subscription")
        print("3. Exit")


        
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
            print("Exiting")
            break    

        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()