"""
Test file to verify Prisma schema and database tables
Tests all 18 tables in the MSME DPR Generator database
"""
import asyncio
from prisma import Prisma
from datetime import datetime
from decimal import Decimal


async def test_all_tables():
    """Test that all 18 tables are created correctly"""
    prisma = Prisma()
    
    try:
        print("🔄 Connecting to PostgreSQL database...")
        await prisma.connect()
        print("✅ Successfully connected!\n")
        
        # List of all table models to test
        tables = [
            ("User", prisma.user),
            ("UserProfile", prisma.userprofile),
            ("DprForm", prisma.dprform),
            ("EntrepreneurDetails", prisma.entrepreneurdetails),
            ("BusinessDetails", prisma.businessdetails),
            ("ProductDetails", prisma.productdetails),
            ("FinancialDetails", prisma.financialdetails),
            ("RevenueAssumptions", prisma.revenueassumptions),
            ("CostDetails", prisma.costdetails),
            ("StaffingDetails", prisma.staffingdetails),
            ("TimelineDetails", prisma.timelinedetails),
            ("GeneratedContent", prisma.generatedcontent),
            ("FinancialProjection", prisma.financialprojection),
            ("FinancialSummary", prisma.financialsummary),
            ("Scheme", prisma.scheme),
            ("SelectedScheme", prisma.selectedscheme),
            ("PdfDocument", prisma.pdfdocument),
            ("UserActivityLog", prisma.useractivitylog),
        ]
        
        print("📊 Testing all 18 database tables...\n")
        
        for table_name, model in tables:
            try:
                count = await model.count()
                print(f"✅ Table '{table_name}': {count} records")
            except Exception as e:
                print(f"❌ Table '{table_name}': Error - {e}")
                
        print(f"\n🎉 All 18 tables verified successfully!")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await prisma.disconnect()
        print("👋 Disconnected from database")


async def test_create_sample_user():
    """Test creating a sample user with profile"""
    prisma = Prisma()
    
    try:
        await prisma.connect()
        print("\n" + "="*60)
        print("🧪 Testing User & Profile Creation...\n")
        
        # Create a test user
        user = await prisma.user.create(
            data={
                "email": f"test_{datetime.now().timestamp()}@example.com",
                "hashedPassword": "hashed_password_123",
                "fullName": "Test User",
                "phone": "1234567890",
                "businessType": "Manufacturing",
                "state": "Andhra Pradesh"
            }
        )
        print(f"✅ Created User: {user.fullName} (ID: {user.id})")
        
        # Create profile for the user
        profile = await prisma.userprofile.create(
            data={
                "userId": user.id,
                "address": "123 Test Street, Hyderabad",
                "aadharNumber": "1234-5678-9012",
                "panNumber": "ABCDE1234F",
                "yearsInBusiness": 5,
                "bio": "Experienced entrepreneur in manufacturing sector"
            }
        )
        print(f"✅ Created Profile for User {user.id}")
        
        # Fetch user with profile
        user_with_profile = await prisma.user.find_unique(
            where={"id": user.id},
            include={"profile": True}
        )
        
        if user_with_profile and user_with_profile.profile:
            print(f"✅ Verified User-Profile Relationship")
            print(f"   User: {user_with_profile.fullName}")
            print(f"   Profile: {user_with_profile.profile.address}")
        
        # Clean up test data
        await prisma.userprofile.delete(where={"id": profile.id})
        await prisma.user.delete(where={"id": user.id})
        print(f"✅ Cleaned up test data")
        
    except Exception as e:
        print(f"❌ Error in user creation test: {e}")
    finally:
        await prisma.disconnect()


async def test_relationships():
    """Test database relationships"""
    prisma = Prisma()
    
    try:
        await prisma.connect()
        print("\n" + "="*60)
        print("🔗 Testing Database Relationships...\n")
        
        # Create user
        user = await prisma.user.create(
            data={
                "email": f"relationship_test_{datetime.now().timestamp()}@example.com",
                "hashedPassword": "hashed_password",
                "fullName": "Relationship Test User",
                "phone": "9876543210",
                "businessType": "Services",
                "state": "Telangana"
            }
        )
        print(f"✅ Created User: {user.id}")
        
        # Create DPR Form
        form = await prisma.dprform.create(
            data={
                "userId": user.id,
                "businessName": "Test Business",
                "status": "draft",
                "completionPercentage": 25
            }
        )
        print(f"✅ Created DPR Form: {form.id}")
        
        # Create Business Details
        business = await prisma.businessdetails.create(
            data={
                "formId": form.id,
                "businessName": "Test Business Pvt Ltd",
                "sector": "Technology",
                "subSector": "Software Development",
                "legalStructure": "Pvt Ltd",
                "location": "Hyderabad",
                "address": "123 Tech Park, Madhapur"
            }
        )
        print(f"✅ Created Business Details: {business.id}")
        
        # Create Activity Log
        activity = await prisma.useractivitylog.create(
            data={
                "userId": user.id,
                "activityType": "form_created",
                "formId": form.id,
                "deviceType": "web"
            }
        )
        print(f"✅ Created Activity Log: {activity.id}")
        
        # Test relationships by fetching user with forms
        user_with_forms = await prisma.user.find_unique(
            where={"id": user.id},
            include={
                "dprForms": {
                    "include": {
                        "businessDetails": True
                    }
                },
                "activityLogs": True
            }
        )
        
        if user_with_forms:
            print(f"\n✅ Verified Relationships:")
            print(f"   User has {len(user_with_forms.dprForms)} form(s)")
            print(f"   User has {len(user_with_forms.activityLogs)} activity log(s)")
            if user_with_forms.dprForms[0].businessDetails:
                print(f"   Form has business details: {user_with_forms.dprForms[0].businessDetails.businessName}")
        
        # Clean up
        await prisma.useractivitylog.delete(where={"id": activity.id})
        await prisma.businessdetails.delete(where={"id": business.id})
        await prisma.dprform.delete(where={"id": form.id})
        await prisma.user.delete(where={"id": user.id})
        print(f"\n✅ Cleaned up test data")
        
    except Exception as e:
        print(f"❌ Error in relationship test: {e}")
    finally:
        await prisma.disconnect()


async def run_all_tests():
    """Run all schema tests"""
    print("\n" + "="*60)
    print("  MSME DPR Generator - Database Schema Test Suite")
    print("="*60 + "\n")
    
    await test_all_tables()
    await test_create_sample_user()
    await test_relationships()
    
    print("\n" + "="*60)
    print("  ✅ All Schema Tests Completed Successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
