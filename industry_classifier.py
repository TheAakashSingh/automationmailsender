"""
Industry Classifier - Identifies company types that need tech support
"""
import re
from typing import List, Dict

# Industry keywords that typically need software/tech support
INDUSTRY_KEYWORDS = {
    'Insurance': [
        'insurance', 'insurer', 'underwriter', 'actuary', 'claims',
        'life insurance', 'health insurance', 'property insurance',
        'auto insurance', 'commercial insurance'
    ],
    'Logistics & Shipping': [
        'logistics', 'shipping', 'freight', 'cargo', 'warehouse',
        '3pl', 'third party logistics', 'supply chain', 'distribution',
        'transportation', 'courier', 'express delivery', 'fulfillment'
    ],
    'Manufacturing': [
        'manufacturing', 'factory', 'production', 'industrial',
        'fabrication', 'assembly', 'packaging'
    ],
    'Healthcare': [
        'hospital', 'clinic', 'medical', 'healthcare', 'health care',
        'physician', 'doctor', 'dental', 'pharmacy', 'laboratory',
        'nursing', 'health services'
    ],
    'Financial Services': [
        'bank', 'financial', 'accounting', 'accountant', 'cpa',
        'tax services', 'bookkeeping', 'audit', 'financial advisor',
        'wealth management', 'investment', 'payroll'
    ],
    'Real Estate': [
        'real estate', 'property management', 'realty', 'realtor',
        'property developer', 'leasing', 'real estate agency'
    ],
    'Retail & E-commerce': [
        'retail', 'store', 'ecommerce', 'e-commerce', 'online store',
        'marketplace', 'merchant', 'shop'
    ],
    'Legal Services': [
        'law firm', 'attorney', 'lawyer', 'legal services', 'legal',
        'litigation', 'law office'
    ],
    'Professional Services': [
        'consulting', 'consultant', 'advisory', 'advisory services',
        'marketing agency', 'advertising agency', 'pr agency',
        'business services', 'professional services'
    ],
    'Education': [
        'school', 'university', 'college', 'education', 'training',
        'academy', 'institute', 'learning'
    ],
    'Construction': [
        'construction', 'contractor', 'building', 'construction company',
        'general contractor', 'construction services'
    ],
    'Hospitality': [
        'hotel', 'restaurant', 'catering', 'hospitality', 'resort',
        'lodging', 'food service'
    ],
    'Automotive': [
        'automotive', 'auto dealer', 'car dealer', 'automotive services',
        'auto repair', 'garage'
    ],
}


def classify_industry(name: str, category: str = '', description: str = '') -> List[str]:
    """
    Classify company industry based on name, category, and description.
    Returns list of matching industry categories.
    """
    text = f"{name} {category} {description}".lower()
    
    matched_industries = []
    
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                if industry not in matched_industries:
                    matched_industries.append(industry)
                break  # Found a match, move to next industry
    
    return matched_industries if matched_industries else ['Other']


def needs_tech_support(industry: str) -> bool:
    """
    Check if an industry typically needs technical/software support.
    """
    tech_needy_industries = [
        'Insurance',
        'Logistics & Shipping',
        'Manufacturing',
        'Healthcare',
        'Financial Services',
        'Real Estate',
        'Retail & E-commerce',
        'Legal Services',
        'Professional Services',
        'Education',
        'Construction',
        'Hospitality',
        'Automotive',
    ]
    
    return industry in tech_needy_industries


def get_primary_industry(industries: List[str]) -> str:
    """Get the primary (first) industry from list."""
    return industries[0] if industries else 'Other'


def enhance_business_with_industry(business: Dict) -> Dict:
    """
    Enhance business data with industry classification.
    """
    name = business.get('name', '')
    category = business.get('category', '')
    description = business.get('description', '')
    
    industries = classify_industry(name, category, description)
    primary_industry = get_primary_industry(industries)
    
    business['industry'] = primary_industry
    business['all_industries'] = ', '.join(industries)
    business['needs_tech_support'] = needs_tech_support(primary_industry)
    
    return business


# Priority industries for software companies (target these first)
PRIORITY_INDUSTRIES = [
    'Insurance',
    'Logistics & Shipping',
    'Healthcare',
    'Financial Services',
    'Manufacturing',
    'Real Estate',
]

