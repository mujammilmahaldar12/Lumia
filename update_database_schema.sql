-- Improved Risk Profiling Schema Updates
-- Run this directly on your PostgreSQL database

-- Add expected_return field to risk_profiles table
ALTER TABLE public.risk_profiles 
ADD COLUMN IF NOT EXISTS expected_return DECIMAL(5,2) DEFAULT 8.0 CHECK (expected_return >= 5.0 AND expected_return <= 15.0);

-- Add age field to help with better profiling
ALTER TABLE public.risk_profiles 
ADD COLUMN IF NOT EXISTS age INTEGER CHECK (age >= 18 AND age <= 100);

-- Add investment_goal field
ALTER TABLE public.risk_profiles 
ADD COLUMN IF NOT EXISTS investment_goal TEXT CHECK (investment_goal IN ('wealth_building', 'retirement', 'education', 'home_purchase', 'emergency_fund', 'other'));

-- Add risk_type field to match roboadvisor
ALTER TABLE public.risk_profiles 
ADD COLUMN IF NOT EXISTS risk_type TEXT CHECK (risk_type IN ('conservative', 'moderate', 'aggressive', 'very_aggressive'));

-- Update the constraint on investment_timeframe to be more specific
ALTER TABLE public.risk_profiles 
DROP CONSTRAINT IF EXISTS risk_profiles_investment_timeframe_check;

ALTER TABLE public.risk_profiles 
ADD CONSTRAINT risk_profiles_investment_timeframe_check 
CHECK (investment_timeframe IN ('1-3 years', '3-5 years', '5-10 years', '10-15 years', '15+ years'));

-- Create an index for better performance on user lookups
CREATE INDEX IF NOT EXISTS idx_risk_profiles_user_id ON public.risk_profiles(user_id);

-- Update any existing data to have default values
UPDATE public.risk_profiles 
SET expected_return = 8.0 
WHERE expected_return IS NULL;

UPDATE public.risk_profiles 
SET risk_type = 'moderate' 
WHERE risk_type IS NULL;

-- Optional: Update investment timeframes to new format if needed
UPDATE public.risk_profiles 
SET investment_timeframe = CASE 
  WHEN investment_timeframe = '1-5 years' THEN '3-5 years'
  WHEN investment_timeframe = '10+ years' THEN '15+ years'
  ELSE investment_timeframe
END;

COMMIT;