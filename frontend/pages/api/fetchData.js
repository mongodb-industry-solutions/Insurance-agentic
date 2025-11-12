export default async function handler(req, res) {
    if (req.method !== "GET") {
      return res.status(405).json({ error: "Method not allowed" });
    }
  
    try {
      // Placeholder for future API call
      // const response = await fetch("https://example.com/api");
      // const data = await response.json();
  
      const data = { message: "API is working. Replace this with real data." };
      res.status(200).json(data);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch data" });
    }
  }
  