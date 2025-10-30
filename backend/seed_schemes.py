"""
Seed script to populate government schemes database
Run this script once to add sample government schemes
"""
import asyncio
from prisma import Prisma
import json

# Sample government schemes for MSMEs in India
GOVERNMENT_SCHEMES = [
    {
        "schemeName": "Prime Minister's Employment Generation Programme (PMEGP)",
        "ministry": "Ministry of MSME",
        "schemeType": "subsidy",
        "description": "PMEGP is a credit-linked subsidy programme for setting up new self-employment ventures/projects/micro enterprises in rural and urban areas. The scheme provides margin money subsidy ranging from 15% to 35% of the project cost.",
        "subsidyPercentage": 35.00,
        "maxSubsidyAmount": 2500000.00,
        "eligibleSectors": ["Manufacturing", "Services", "Trading", "All Sectors"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 100000.00,
        "maxInvestment": 10000000.00,
        "eligibilityCriteria": "Indian citizen above 18 years; No income limit for general category; Minimum 8th pass for projects costing above Rs. 10 lakhs in manufacturing sector and above Rs. 5 lakhs in service sector; Only new projects are eligible.",
        "applicationLink": "https://www.kviconline.gov.in/pmegpeportal/"
    },
    {
        "schemeName": "Credit Guarantee Scheme for Micro and Small Enterprises (CGMSE)",
        "ministry": "Ministry of MSME",
        "schemeType": "loan",
        "description": "CGMSE provides collateral-free credit to micro and small enterprises. The scheme covers both term loans and working capital facilities. Credit guarantee of 85% for loans up to Rs. 5 lakhs and 75% for loans above Rs. 5 lakhs.",
        "subsidyPercentage": None,
        "maxSubsidyAmount": None,
        "eligibleSectors": ["Manufacturing", "Services", "All Sectors"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 100000.00,
        "maxInvestment": 20000000.00,
        "eligibilityCriteria": "New and existing Micro and Small Enterprises; Existing units should be satisfactorily operational; Unit should not be in default to any bank/financial institution.",
        "applicationLink": "https://www.cgtmse.in/"
    },
    {
        "schemeName": "Credit Linked Capital Subsidy Scheme (CLCSS)",
        "ministry": "Ministry of MSME",
        "schemeType": "subsidy",
        "description": "CLCSS provides 15% capital subsidy (limited to Rs. 15 lakhs) to MSMEs on institutional finance of up to Rs. 1 crore for induction of well-established and improved technology in the specified products.",
        "subsidyPercentage": 15.00,
        "maxSubsidyAmount": 1500000.00,
        "eligibleSectors": ["Manufacturing"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 1000000.00,
        "maxInvestment": 10000000.00,
        "eligibilityCriteria": "Existing and new MSMEs; Must upgrade to specified approved technology; Should have been in operation for at least 3 years.",
        "applicationLink": "https://msme.gov.in/clcss"
    },
    {
        "schemeName": "Stand-Up India Scheme",
        "ministry": "Department of Financial Services",
        "schemeType": "loan",
        "description": "Stand-Up India facilitates bank loans between Rs. 10 lakh and Rs. 1 crore to at least one SC/ST borrower and at least one woman borrower per bank branch for setting up a greenfield enterprise in manufacturing, services or trading sector.",
        "subsidyPercentage": None,
        "maxSubsidyAmount": None,
        "eligibleSectors": ["Manufacturing", "Services", "Trading", "All Sectors"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 1000000.00,
        "maxInvestment": 10000000.00,
        "eligibilityCriteria": "SC/ST and/or Women entrepreneurs above 18 years of age; Loan for greenfield project; In case of non-individual enterprises, at least 51% shareholding and controlling stake should be with SC/ST/Woman entrepreneur.",
        "applicationLink": "https://www.standupmitra.in/"
    },
    {
        "schemeName": "Mudra Loan - Shishu Category",
        "ministry": "Ministry of Finance",
        "schemeType": "loan",
        "description": "MUDRA Shishu loans are provided for business activities whose loan requirement is up to Rs. 50,000. These loans are typically for small entrepreneurs and business startups.",
        "subsidyPercentage": None,
        "maxSubsidyAmount": None,
        "eligibleSectors": ["Manufacturing", "Services", "Trading", "Agriculture", "All Sectors"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 10000.00,
        "maxInvestment": 50000.00,
        "eligibilityCriteria": "Small business owners; Non-farm income generating activities; Individual or group of individuals; Income generating micro/small business enterprises.",
        "applicationLink": "https://www.mudra.org.in/"
    },
    {
        "schemeName": "Mudra Loan - Kishore Category",
        "ministry": "Ministry of Finance",
        "schemeType": "loan",
        "description": "MUDRA Kishore loans are for businesses that are well established and looking to expand. Loan amount ranges from Rs. 50,001 to Rs. 5 lakhs.",
        "subsidyPercentage": None,
        "maxSubsidyAmount": None,
        "eligibleSectors": ["Manufacturing", "Services", "Trading", "Agriculture", "All Sectors"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 50001.00,
        "maxInvestment": 500000.00,
        "eligibilityCriteria": "Business in operation; Income generating activities; Good credit history; Viable business plan.",
        "applicationLink": "https://www.mudra.org.in/"
    },
    {
        "schemeName": "Mudra Loan - Tarun Category",
        "ministry": "Ministry of Finance",
        "schemeType": "loan",
        "description": "MUDRA Tarun loans are for well-established businesses looking for significant expansion. Loan amount ranges from Rs. 5 lakhs to Rs. 10 lakhs.",
        "subsidyPercentage": None,
        "maxSubsidyAmount": None,
        "eligibleSectors": ["Manufacturing", "Services", "Trading", "Agriculture", "All Sectors"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 500001.00,
        "maxInvestment": 1000000.00,
        "eligibilityCriteria": "Established business; Income generating activities; Good repayment track record; Business expansion plan.",
        "applicationLink": "https://www.mudra.org.in/"
    },
    {
        "schemeName": "Technology Upgradation Fund Scheme (TUFS)",
        "ministry": "Ministry of Textiles",
        "schemeType": "subsidy",
        "description": "TUFS provides capital subsidy for technology upgradation of the textile and jute industry. The scheme aims to facilitate increased investment for modernization of the textile industry.",
        "subsidyPercentage": 15.00,
        "maxSubsidyAmount": 3000000.00,
        "eligibleSectors": ["Textile", "Manufacturing"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 2000000.00,
        "maxInvestment": 50000000.00,
        "eligibilityCriteria": "Textile and jute manufacturing units; Technology upgradation investment; Must be registered as MSME.",
        "applicationLink": "https://texmin.nic.in/tufs"
    },
    {
        "schemeName": "Telangana State Industrial Project Approval System (TS-iPASS)",
        "ministry": "Government of Telangana",
        "schemeType": "subsidy",
        "description": "TS-iPASS provides single-window clearance system and various incentives including capital subsidy, power subsidy, and stamp duty exemption for industrial units in Telangana.",
        "subsidyPercentage": 25.00,
        "maxSubsidyAmount": 5000000.00,
        "eligibleSectors": ["Manufacturing", "Services", "IT", "All Sectors"],
        "eligibleStates": ["Telangana", "Hyderabad"],
        "minInvestment": 500000.00,
        "maxInvestment": 100000000.00,
        "eligibilityCriteria": "New industrial units in Telangana; Manufacturing or service sector; Minimum employment generation; Land allotment in industrial parks.",
        "applicationLink": "https://ipass.telangana.gov.in/"
    },
    {
        "schemeName": "Startup India Seed Fund Scheme (SISFS)",
        "ministry": "Department for Promotion of Industry and Internal Trade",
        "schemeType": "grant",
        "description": "SISFS provides financial assistance to startups for proof of concept, prototype development, product trials, market entry, and commercialization. Grant up to Rs. 20 lakhs for validation of Proof of Concept.",
        "subsidyPercentage": None,
        "maxSubsidyAmount": 2000000.00,
        "eligibleSectors": ["Technology", "Innovation", "Manufacturing", "Services", "All Sectors"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 100000.00,
        "maxInvestment": 5000000.00,
        "eligibilityCriteria": "DPIIT recognized startups; Incorporated less than 2 years ago; Working on innovative product/service with market potential; Should not have received more than Rs. 10 lakh of monetary support from Government.",
        "applicationLink": "https://seedfund.startupindia.gov.in/"
    },
    {
        "schemeName": "Pradhan Mantri Formalization of Micro Food Processing Enterprises (PMFME)",
        "ministry": "Ministry of Food Processing Industries",
        "schemeType": "subsidy",
        "description": "PMFME provides credit-linked capital subsidy of 35% (maximum Rs. 10 lakhs) for setting up or upgrading food processing units. The scheme also provides technical and business support.",
        "subsidyPercentage": 35.00,
        "maxSubsidyAmount": 1000000.00,
        "eligibleSectors": ["Food Processing", "Manufacturing"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 100000.00,
        "maxInvestment": 10000000.00,
        "eligibilityCriteria": "Existing micro food processing units; Farmer Producer Organizations (FPOs); Self Help Groups (SHGs); Cooperatives; Individual entrepreneurs; Should have FSSAI license or should be willing to obtain it.",
        "applicationLink": "https://pmfme.mofpi.gov.in/"
    },
    {
        "schemeName": "National Manufacturing Competitiveness Programme (NMCP)",
        "ministry": "Ministry of MSME",
        "schemeType": "training",
        "description": "NMCP provides support for technology upgradation, quality certification, marketing support, skill development, and lean manufacturing initiatives for MSMEs to enhance their competitiveness.",
        "subsidyPercentage": None,
        "maxSubsidyAmount": 500000.00,
        "eligibleSectors": ["Manufacturing", "All Sectors"],
        "eligibleStates": ["All States", "Pan India"],
        "minInvestment": 50000.00,
        "maxInvestment": 20000000.00,
        "eligibilityCriteria": "Existing MSMEs; Must be registered; Willing to adopt modern manufacturing practices; Quality certification.",
        "applicationLink": "https://msme.gov.in/nmcp"
    }
]


async def seed_schemes():
    """Populate the database with government schemes"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🌱 Starting to seed government schemes...")
        
        # Check if schemes already exist
        existing_count = await prisma.scheme.count()
        if existing_count > 0:
            print(f"⚠️  Database already has {existing_count} scheme(s).")
            response = input("Do you want to delete existing schemes and reseed? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Seeding cancelled.")
                return
            
            # Delete existing schemes
            deleted = await prisma.scheme.delete_many()
            print(f"🗑️  Deleted {deleted} existing scheme(s).")
        
        # Insert schemes
        created_count = 0
        for scheme_data in GOVERNMENT_SCHEMES:
            # Convert lists to JSON format for Prisma
            scheme_create_data = {
                **scheme_data,
                "eligibleSectors": json.dumps(scheme_data["eligibleSectors"]),
                "eligibleStates": json.dumps(scheme_data["eligibleStates"])
            }
            await prisma.scheme.create(data=scheme_create_data)
            created_count += 1
            print(f"✅ Created: {scheme_data['schemeName']}")
        
        print(f"\n🎉 Successfully seeded {created_count} government schemes!")
        
        # Show summary
        total_schemes = await prisma.scheme.count()
        print(f"\n📊 Database Summary:")
        print(f"   Total schemes: {total_schemes}")
        
        # Show schemes by type
        subsidy_count = await prisma.scheme.count(where={"schemeType": "subsidy"})
        loan_count = await prisma.scheme.count(where={"schemeType": "loan"})
        grant_count = await prisma.scheme.count(where={"schemeType": "grant"})
        training_count = await prisma.scheme.count(where={"schemeType": "training"})
        
        print(f"   - Subsidy schemes: {subsidy_count}")
        print(f"   - Loan schemes: {loan_count}")
        print(f"   - Grant schemes: {grant_count}")
        print(f"   - Training schemes: {training_count}")
        
    except Exception as e:
        print(f"❌ Error seeding schemes: {str(e)}")
        raise
    finally:
        await prisma.disconnect()


if __name__ == "__main__":
    asyncio.run(seed_schemes())
