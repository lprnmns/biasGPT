export const samplePositions = [
  {
    id: "pos-1",
    asset: "BTC-USDT",
    side: "LONG",
    entryPrice: "42500",
    size: "0.5 BTC",
    pnl: "+$1,250"
  },
  {
    id: "pos-2",
    asset: "ETH-USDT",
    side: "SHORT",
    entryPrice: "2300",
    size: "5 ETH",
    pnl: "-$320"
  }
];

export const sampleBias = [
  { asset: "BTC", value: "+0.35", confidence: "0.82" },
  { asset: "ETH", value: "-0.15", confidence: "0.64" }
];

export const sampleWhaleEvents = [
  {
    txHash: "0xabc",
    wallet: "0xWhale1",
    action: "deposited",
    amount: "500",
    asset: "ETH",
    timestamp: "2025-01-01T00:00:00Z"
  },
  {
    txHash: "0xdef",
    wallet: "0xWhale2",
    action: "withdrew",
    amount: "1500",
    asset: "BTC",
    timestamp: "2025-01-01T01:30:00Z"
  }
];

export const sampleChatHistory = [
  {
    role: "assistant",
    content: "Whale deposit detected; bias leaning bearish for BTC.",
    citations: ["evt_123", "evt_456"],
    confidence: 0.78
  },
  {
    role: "user",
    content: "Should we hedge our ETH exposure?",
    citations: [],
    confidence: null
  }
];
