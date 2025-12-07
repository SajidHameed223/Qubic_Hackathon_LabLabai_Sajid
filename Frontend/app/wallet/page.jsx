"use client";
import { useState, useEffect } from "react";
import {
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  Copy,
  Send,
  Download,
  X,
} from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";

export default function WalletComponent() {
  const [balance, setBalance] = useState(0);
  // Receive form state
  const [senderName, setSenderName] = useState("");
  const [receiveAmount, setReceiveAmount] = useState("");
  const [transactions, setTransactions] = useState([]);
  const [showError, setShowError] = useState(false);
  const [walletAddress] = useState("0x1234...abcd"); // mock address
  // Generate random 8-digit ID
  const generateId = () =>
    Math.floor(10000000 + Math.random() * 90000000).toString();
  // Popup states
  const [showReceive, setShowReceive] = useState(false);
  const [showSend, setShowSend] = useState(false);

  // Send form state
  const [recipient, setRecipient] = useState("");
  const [amount, setAmount] = useState("");

  useEffect(() => {
    // In real project: fetch from Qubic API
    setBalance(1250.75);
    setTransactions([
      {
        id: 23456789,
        type: "credit",
        amount: 200,
        date: "2025-12-05",
        desc: "Received from Alice",
      },
      {
        id: 34567890,
        type: "debit",
        amount: 50,
        date: "2025-12-04",
        desc: "Sent to Bob",
      },
      {
        id: 19876543,
        type: "credit",
        amount: 100,
        date: "2025-12-03",
        desc: "Reward payout",
      },
    ]);
  }, []);

  const copyAddress = () => {
    navigator.clipboard.writeText(walletAddress);
    alert("Wallet address copied!");
  };

  const handleSendQubic = () => {
    if (!recipient || !amount || !senderName) {
      alert("Please enter sender name, recipient address and amount");
      return;
    }
    if (parseFloat(amount) > balance) {
        setShowSend(false);   // close send popup
        setShowError(true);   // show error popup
        return;
      }
    
    const newTx = {
      id: generateId(),
      type: "debit",
      amount: parseFloat(amount),
      date: new Date().toISOString().split("T")[0],
      desc: `Sent by ${senderName} to ${recipient}`,
    };
    setTransactions((prev) => [newTx, ...prev]);
    setBalance((prev) => prev - parseFloat(amount));
    alert(`Sent ${amount} QUBIC to ${recipient} (Sender: ${senderName})`);
    setShowSend(false);
    setRecipient("");
    setAmount("");
    setSenderName("");
  };
  const handleReceiveQubic = () => {
    if (!senderName || !receiveAmount) {
      alert("Please enter sender name and amount");
      return;
    }
    const newTx = {
      id: generateId(),
      type: "credit",
      amount: parseFloat(receiveAmount),
      date: new Date().toISOString().split("T")[0],
      desc: `Received from ${senderName}`,
    };
    setTransactions((prev) => [newTx, ...prev]);
    setBalance((prev) => prev + parseFloat(receiveAmount));
    alert(`Received ${receiveAmount} QUBIC from ${senderName}`);
    setShowReceive(false);
    setSenderName("");
    setReceiveAmount("");
  };

  return (
    <DashboardLayout>
      <div className="max-w-md mx-auto bg-white shadow-lg rounded-xl p-6 space-y-6">
        {/* Balance Section */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Wallet className="w-6 h-6 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-600">My Wallet</h2>
          </div>
          <span className="text-2xl font-bold text-green-600">
            {balance.toLocaleString()} QUBIC
          </span>
        </div>

        {/* Wallet Address */}
        <div className="flex items-center justify-between bg-gray-100 p-2 rounded-lg">
          <span className="text-sm font-mono text-gray-400">
            {walletAddress}
          </span>
          <button
            onClick={copyAddress}
            className="p-1 hover:bg-gray-200 rounded"
          >
            <Copy className="w-4 h-4 text-gray-600" />
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <button
            onClick={() => setShowSend(true)}
            className="flex-1 flex items-center justify-center bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600"
          >
            <Send className="w-4 h-4 mr-2" /> Send
          </button>
          <button
            onClick={() => setShowReceive(true)}
            className="flex-1 flex items-center justify-center bg-green-500 text-white py-2 rounded-lg hover:bg-green-600"
          >
            <Download className="w-4 h-4 mr-2" /> Receive
          </button>
        </div>

        {/* Transactions Section */}
        <div>
          <h3 className="text-md font-semibold mb-3 text-gray-600">
            Latest Transactions
          </h3>
          <ul className="space-y-3">
            {transactions.map((tx) => (
              <li
                key={tx.id}
                className="flex items-center justify-between border-b pb-2"
              >
                <div className="flex items-center space-x-2">
                  {tx.type === "credit" ? (
                    <ArrowDownRight className="w-5 h-5 text-green-500" />
                  ) : (
                    <ArrowUpRight className="w-5 h-5 text-red-500" />
                  )}
                  <div>
                    <p className="text-xs text-gray-500">
                      {" "}
                      {tx.date} | ID: {tx.id}
                    </p>
                    <p className="text-sm font-medium text-gray-600">
                      {tx.desc}
                    </p>
                  </div>
                </div>
                <span
                  className={`font-semibold ${
                    tx.type === "credit" ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {tx.type === "credit" ? "+" : "-"}
                  {tx.amount} QUBIC
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      {/* Error Popup */}
      {showError && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 w-96 relative">
            <button
              onClick={() => setShowError(false)}
              className="absolute top-2 right-2 text-gray-600 hover:text-black"
            >
              <X className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-semibold mb-4 text-red-600">
              Not Enough Balance
            </h2>
            <p className="text-sm text-gray-600">
              You tried to send more QUBIC than your current balance ({balance}{" "}
              QUBIC).
            </p>
            <button
              onClick={() => setShowError(false)}
              className="mt-4 w-full bg-red-500 text-white py-2 rounded-lg hover:bg-red-600"
            >
              Close
            </button>
          </div>
        </div>
      )}
      {/* Receive Popup */}
      {showReceive && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 w-96 relative">
            <button
              onClick={() => setShowReceive(false)}
              className="absolute top-2 right-2 text-gray-600 hover:text-black"
            >
              <X className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-semibold mb-4 text-gray-600">
              Receive QUBIC
            </h2>
            <p className="text-sm mb-2 text-gray-500">
              Share your wallet address with the sender. Copy it below:
            </p>
            <div className="flex items-center justify-between bg-gray-100 p-2 rounded-lg mb-4">
              <span className="text-sm font-mono text-gray-400">
                {walletAddress}
              </span>
              <button
                onClick={copyAddress}
                className="p-1 hover:bg-gray-200 rounded"
              >
                <Copy className="w-4 h-4 text-gray-600" />
              </button>
            </div>

            {/* Receive form */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-600">
                  Sender Name
                </label>
                <input
                  type="text"
                  value={senderName}
                  onChange={(e) => setSenderName(e.target.value)}
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-green-500 text-gray-400"
                  placeholder="Enter sender name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-600">
                  Amount
                </label>
                <input
                  type="number"
                  value={receiveAmount}
                  onChange={(e) => setReceiveAmount(e.target.value)}
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-green-500 text-gray-400"
                  placeholder="Enter amount"
                />
              </div>
              <button
                onClick={handleReceiveQubic}
                className="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600"
              >
                Receive QUBIC
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Send Popup */}
      {showSend && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 w-96 relative">
            <button
              onClick={() => setShowSend(false)}
              className="absolute top-2 right-2 text-gray-600 hover:text-black"
            >
              <X className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-semibold mb-4 text-gray-600">
              Send QUBIC
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-600">
                  Sender Name
                </label>
                <input
                  type="text"
                  value={senderName}
                  onChange={(e) => setSenderName(e.target.value)}
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-400"
                  placeholder="Enter your name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-600">
                  Recipient Address
                </label>
                <input
                  type="text"
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-400"
                  placeholder="Enter recipient wallet address"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-600">
                  Amount
                </label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-400"
                  placeholder="Enter amount"
                />
              </div>
              <button
                onClick={handleSendQubic}
                className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600"
              >
                Send QUBIC
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
