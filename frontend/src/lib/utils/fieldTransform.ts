/**
 * Utility functions to transform field names between camelCase (frontend) and snake_case (backend)
 */

// Transform snake_case to camelCase (for loading data from backend)
export function snakeToCamel(obj: any): any {
  if (!obj || typeof obj !== 'object') return obj;
  
  if (Array.isArray(obj)) {
    return obj.map(item => snakeToCamel(item));
  }
  
  const transformed: any = {};
  
  for (const [key, value] of Object.entries(obj)) {
    // Convert snake_case to camelCase
    const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    transformed[camelKey] = typeof value === 'object' && value !== null 
      ? snakeToCamel(value) 
      : value;
  }
  
  return transformed;
}

// Transform camelCase to snake_case (for sending data to backend)
export function camelToSnake(obj: any): any {
  if (!obj || typeof obj !== 'object') return obj;
  
  if (Array.isArray(obj)) {
    return obj.map(item => camelToSnake(item));
  }
  
  const transformed: any = {};
  
  for (const [key, value] of Object.entries(obj)) {
    // Convert camelCase to snake_case
    const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
    transformed[snakeKey] = typeof value === 'object' && value !== null 
      ? camelToSnake(value) 
      : value;
  }
  
  return transformed;
}

// Specific transformations for each section (Backend → Frontend)
export const transformEntrepreneurDetails = (data: any) => {
  if (!data) return null;
  return {
    fullName: data.full_name,
    dateOfBirth: data.date_of_birth,
    education: data.education,
    yearsOfExperience: data.years_of_experience,
    previousBusinessExperience: data.previous_business_experience,
    technicalSkills: data.technical_skills,
  };
};

export const transformBusinessDetails = (data: any) => {
  if (!data) return null;
  return {
    businessName: data.business_name,
    sector: data.sector,
    subSector: data.sub_sector,
    legalStructure: data.legal_structure,
    registrationNumber: data.registration_number,
    location: data.location,
    address: data.address,
  };
};

export const transformProductDetails = (data: any) => {
  if (!data) return null;
  
  // Convert array of features to newline-separated string
  let keyFeaturesString = '';
  if (data.key_features && Array.isArray(data.key_features)) {
    keyFeaturesString = data.key_features.join('\n');
  }
  
  return {
    productName: data.product_name,
    description: data.description,
    keyFeatures: keyFeaturesString,
    targetCustomers: data.target_customers,
    currentCapacity: data.current_capacity,
    plannedCapacity: data.planned_capacity,
    uniqueSellingPoints: data.unique_selling_points,
    qualityCertifications: data.quality_certifications,
  };
};

export const transformFinancialDetails = (data: any) => {
  if (!data) return null;
  return {
    totalInvestmentAmount: data.total_investment_amount,
    landCost: data.land_cost,
    buildingCost: data.building_cost,
    machineryCost: data.machinery_cost,
    otherAssetsCost: data.other_assets_cost,
    workingCapital: data.working_capital,
    ownContribution: data.own_contribution,
    loanAmount: data.loan_amount,
    loanInterestRate: data.loan_interest_rate,
    loanTenureMonths: data.loan_tenure_months,
  };
};

export const transformRevenueAssumptions = (data: any) => {
  if (!data) return null;
  return {
    productPrice: data.product_price,
    monthlySalesYear1: data.monthly_sales_quantity_year1,
    monthlySalesYear2: data.monthly_sales_quantity_year2,
    monthlySalesYear3: data.monthly_sales_quantity_year3,
    growthRate: data.growth_rate_percentage,
  };
};

export const transformCostDetails = (data: any) => {
  if (!data) return null;
  return {
    monthlyRawMaterial: data.raw_material_cost_monthly,
    monthlyLabor: data.labor_cost_monthly,
    monthlyUtilities: data.utilities_cost_monthly,
    monthlyRent: data.rent_monthly,
    monthlyMarketing: data.marketing_cost_monthly,
    otherFixedCosts: data.other_fixed_costs_monthly,
  };
};

export const transformStaffingDetails = (data: any) => {
  if (!data) return null;
  return {
    totalEmployees: data.total_employees,
    managementCount: data.management_count,
    technicalStaffCount: data.technical_staff_count,
    supportStaffCount: data.support_staff_count,
    averageSalary: data.average_salary,
  };
};

export const transformTimelineDetails = (data: any) => {
  if (!data) return null;
  return {
    landAcquisitionMonths: data.land_acquisition_months,
    constructionMonths: data.construction_months,
    machineryInstallationMonths: data.machinery_installation_months,
    trialProductionMonths: data.trial_production_months,
    commercialProductionStartMonth: data.commercial_production_start_month,
  };
};
