
from utils import add_tenant

def main():
    while True:
        print("\n--- SaaS Billing Console ---")
        print("1. Add Tenant")
        print("2. Exit")


        
        choice = input("Choose an option: ")

        if choice == "1":
            name = input("Tenant Name: ")
            tenant = add_tenant(name)
            print(f"Tenant Added: {tenant}")

        elif choice == "2":
            print("Exiting")
            break    

        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()