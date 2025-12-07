
import httpx
import time
import uuid

BASE_URL = "http://localhost:8000"

def run_demo():
    print("🚀 Starting Agent Trade Demo...")
    
    # Unique user for this run
    email = f"trader_{str(uuid.uuid4())[:8]}@example.com"
    password = "secret_password"
    
    print(f"\n1️⃣  Registering User: {email}")
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        # Register
        resp = client.post("/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Demo Trader"
        })
        if resp.status_code not in (200, 201):
            print(f"❌ Registration failed: {resp.text} (Status: {resp.status_code})")
            return
            
        # Login
        print("🔑 Logging In...")
        resp = client.post("/auth/login", json={
            "email": email,
            "password": password
        })
        token = resp.json().get("access_token")
        if not token:
            print(f"❌ Login succeeded but no token found: {resp.json()}")
            return
            
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Logged in successfully.")
        
        # Check Initial Balance
        print("\n💰 Checking Initial Balance...")
        wallet_resp = client.get("/wallet/balance?asset=QUBIC", headers=headers)
        if wallet_resp.status_code != 200:
             print(f"❌ Balance Check Failed: {wallet_resp.text}")
        else:
             print(f"Balance: {wallet_resp.json()}")
        
        # Deposit Funds (Mock)
        print("\n📥 Depositing 1,000,000 QUBIC (via Mock TX)...")
        # Transaction ID mapped to 1M QUBIC in our fallback logic
        tx_id = "uomvcfcjpcveqfdcikrjrjwdmoqenrilfxdjsewdsdkyhjonjhvazsregqib"
        resp = client.post("/wallet/deposit/confirm", headers=headers, json={
            "tx_hash": tx_id,
            "amount": 1000000
        })
        if resp.status_code == 200:
            print(f"✅ Deposit Confirmed: {resp.json()}")
        else:
            print(f"❌ Deposit Failed: {resp.text}")
            return

        # Check Balance Again
        resp = client.get("/wallet/balance/QUBIC", headers=headers)
        bal = resp.json()
        print(f"💰 New Balance: {bal.get('available')} QUBIC")
        
        # Execute Agent Trade
        amount_to_send = 5000
        dest = "BAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBAA"
        goal = f"Send {amount_to_send} QUBIC to {dest}"
        
        print(f"\n🤖 Instructing Agent: '{goal}'")
        print("... Agent is planning and executing (this might take a few seconds) ...")
        
        resp = client.post("/agent/run", headers=headers, json={
            "goal": goal,
            "dry_run": False
        })
        
        if resp.status_code != 200:
            print(f"❌ Agent Task Failed: {resp.text}")
            return
            
        task = resp.json()
        status = task.get("status")
        print(f"📋 Task Status: {status}")
        
        if status == "PENDING_APPROVAL":
            approval_id = task.get("approval_id")
            print(f"⚠️  Task requires approval (ID: {approval_id})")
            print("👍 Auto-approving for demo purposes...")
            
            # Approve
            approve_resp = client.post(
                f"/approvals/approve/{approval_id}", 
                headers=headers, 
                json={
                    "approval_id": approval_id,
                    "decision": "approve",
                    "note": "Auto-approved by demo script"
                }
            )
            if approve_resp.status_code == 200:
                print("✅ Approved successfully.")
            else:
                 print(f"❌ Approval failed: {approve_resp.text}")
                 return

            # Execute Approved
            print("🚀 Triggering execution of approved task...")
            exec_resp = client.post(f"/agent/execute-approved/{approval_id}", headers=headers)
            if exec_resp.status_code == 200:
                task = exec_resp.json()
                status = task.get("status")
                print(f"📋 Updated Task Status: {status}")
            else:
                print(f"❌ Execution trigger failed: {exec_resp.text}")
                return

        # Check logs/result
        if status == "COMPLETED":
            print("✅ Agent executed trade successfully!")
            for log in task.get("logs", [])[-3:]:
                print(f"   Log: {log}")
        else:
             print(f"⚠️ Task did not complete instantly. Status: {status}")
             for log in task.get("logs", []):
                print(f"   Log: {log}")
                
        # Final Balance Check
        print("\n🔍 Verifying Final Balance...")
        resp = client.get("/wallet/balance?asset=QUBIC", headers=headers)
        final_bal = resp.json().get("available")
        print(f"💰 Final Balance: {final_bal} QUBIC")
        
        expected = 1000000 - amount_to_send
        if float(final_bal) == float(expected):
            print("✅ SUCCESS: Balance matches expected amount!")
        else:
            print(f"⚠️ Warning: Expected {expected}, got {final_bal}")

if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        print("Note: Ensure the backend server is running on localhost:8000")
