-- Complete Database Update Script for Lumia RoboAdvisor
-- Run this on your Supabase/PostgreSQL database to enable all new features

-- Step 1: Add new columns to risk_profiles table
ALTER TABLE public.risk_profiles 
ADD COLUMN IF NOT EXISTS expected_return DECIMAL(5,2) DEFAULT 8.0 CHECK (expected_return >= 5.0 AND expected_return <= 15.0);

ALTER TABLE public.risk_profiles 
ADD COLUMN IF NOT EXISTS age INTEGER CHECK (age >= 18 AND age <= 100);

ALTER TABLE public.risk_profiles 
ADD COLUMN IF NOT EXISTS investment_goal TEXT CHECK (investment_goal IN ('wealth_building', 'retirement', 'education', 'home_purchase', 'emergency_fund', 'other'));

ALTER TABLE public.risk_profiles 
ADD COLUMN IF NOT EXISTS risk_type TEXT CHECK (risk_type IN ('conservative', 'moderate', 'aggressive', 'very_aggressive'));

-- Step 2: Update investment_timeframe constraint to support new options
ALTER TABLE public.risk_profiles 
DROP CONSTRAINT IF EXISTS risk_profiles_investment_timeframe_check;

ALTER TABLE public.risk_profiles 
ADD CONSTRAINT risk_profiles_investment_timeframe_check 
CHECK (investment_timeframe IN ('1-3 years', '3-5 years', '5-10 years', '10-15 years', '15+ years', '1-5 years', '10+ years'));

-- Step 3: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_risk_profiles_user_id ON public.risk_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_financial_goals_user_id ON public.financial_goals(user_id);

-- Step 4: Update any existing data with default values
UPDATE public.risk_profiles 
SET expected_return = 8.0 
WHERE expected_return IS NULL;

UPDATE public.risk_profiles 
SET risk_type = CASE 
  WHEN risk_tolerance <= 3 THEN 'conservative'
  WHEN risk_tolerance <= 6 THEN 'moderate'
  WHEN risk_tolerance <= 8 THEN 'aggressive'
  ELSE 'very_aggressive'
END
WHERE risk_type IS NULL;

-- Step 5: Verify the changes
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'risk_profiles' 
AND table_schema = 'public'
ORDER BY ordinal_position;

COMMIT;

-- Test query to see all profile data
-- SELECT * FROM public.risk_profiles LIMIT 5;