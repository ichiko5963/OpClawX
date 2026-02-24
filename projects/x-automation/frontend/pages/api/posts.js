// API Routes for X Automation
import { NextApiRequest, NextApiResponse } from 'next'

// In-memory storage (in production, use database)
let generatedPosts = []
let trendingPosts = []

export default async function handler(req, res) {
  const { method } = req

  switch (method) {
    case 'GET':
      return handleGet(req, res)
    case 'POST':
      return handlePost(req, res)
    default:
      res.setHeader('Allow', ['GET', 'POST'])
      res.status(405).end(`Method ${method} Not Allowed`)
  }
}

async function handleGet(req, res) {
  res.status(200).json({
    generated: generatedPosts,
    trending: trendingPosts
  })
}

async function handlePost(req, res) {
  const { text, media } = req.body
  
  // In production, call X API here
  // For now, simulate success
  console.log('Posting to X:', text.substring(0, 100))
  
  res.status(200).json({
    success: true,
    post_id: 'mock_' + Date.now()
  })
}
