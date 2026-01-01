import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { parse } from 'csv-parse/sync'
import { Readable } from 'stream'

export async function POST(request: Request) {
  const session = await getServerSession(authOptions)

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const formData = await request.formData()
    const file = formData.get('file') as File

    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 })
    }

    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    const text = buffer.toString('utf-8')

    // Parse CSV
    const records = parse(text, {
      columns: true,
      skip_empty_lines: true,
      trim: true,
    })

    let added = 0
    let duplicates = 0
    let errors = 0

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    for (const record of records) {
      try {
        // Validate required fields
        if (!record.company || !record.email) {
          errors++
          continue
        }

        // Validate email format
        if (!emailRegex.test(record.email)) {
          errors++
          continue
        }

        // Check if lead already exists (by email)
        const existing = await prisma.lead.findFirst({
          where: { email: record.email.toLowerCase() },
        })

        if (existing) {
          duplicates++
          continue
        }

        // Determine industry from keyword or use provided
        let industry = record.industry || ''
        if (!industry && record.company) {
          const companyLower = record.company.toLowerCase()
          if (companyLower.includes('insurance')) industry = 'Insurance'
          else if (companyLower.includes('logistics') || companyLower.includes('shipping') || companyLower.includes('freight')) industry = 'Logistics & Shipping'
          else if (companyLower.includes('health') || companyLower.includes('medical') || companyLower.includes('hospital')) industry = 'Healthcare'
          else if (companyLower.includes('financial') || companyLower.includes('bank') || companyLower.includes('accounting')) industry = 'Financial Services'
          else if (companyLower.includes('real estate') || companyLower.includes('property')) industry = 'Real Estate'
          else if (companyLower.includes('manufacturing') || companyLower.includes('factory')) industry = 'Manufacturing'
        }

        // Create tags based on industry and country
        const tags: string[] = []
        if (industry) tags.push(industry)
        if (record.country) tags.push(record.country)
        if (record.city) tags.push(record.city)

        // Create lead
        await prisma.lead.create({
          data: {
            company: record.company.trim(),
            email: record.email.toLowerCase().trim(),
            phone: record.phone?.trim() || null,
            website: record.website?.trim() || null,
            city: record.city?.trim() || null,
            country: record.country?.trim() || null,
            industry: industry || null,
            tags,
            status: 'pending',
          },
        })

        added++
      } catch (error) {
        console.error('Error processing lead:', error)
        errors++
      }
    }

    return NextResponse.json({
      success: true,
      added,
      duplicates,
      errors,
      total: records.length,
    })
  } catch (error: any) {
    console.error('Error uploading CSV:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to process CSV' },
      { status: 500 }
    )
  }
}

