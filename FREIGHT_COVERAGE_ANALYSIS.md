# Freight Intelligence Platform - Coverage Analysis

**Date:** 2025-12-03
**Scope:** US LTL & TL Freight - Spot Orders & Contract Lanes
**Focus:** Actionable Intelligence with Real Data

---

## Executive Summary

Current platform coverage: **~5% of required intelligence**

**CRITICAL ISSUE:** ~95% of current data is synthetically generated (fake). This provides **zero actionable intelligence** for freight decision-making.

**Primary Gap:** Platform lacks real spot rates, contract lane pricing, capacity data, and geographic granularity necessary for actual freight procurement and planning decisions.

---

## Current State Assessment

### ✅ What Works (Minimal)
1. **Diesel Fuel Prices** - Real EIA data (web scraping)
2. **News Aggregation** - 4 RSS feeds providing industry context
3. **Technical Architecture** - Functional data pipeline and dashboard

### ❌ Critical Failures
1. **Spot Rates** - 100% fake/synthetic data
2. **Macro Indices** - 100% fake/synthetic data
3. **No LTL Coverage** - Platform only addresses TL (Van/Reefer/Flatbed)
4. **No Geographic Data** - National averages only, no lane-specific intelligence
5. **No Contract Rate Tracking** - Only synthetic spot data exists
6. **No Capacity Indicators** - No load-to-truck ratios, rejection rates, or availability metrics

---

## Required Data Coverage for Actionable Intelligence

### 1. **SPOT MARKET RATES** (Currently: Fake Data ❌)

#### What's Needed:
- **TL Spot Rates** by lane (origin-destination pairs)
  - Dry Van rates per mile
  - Reefer rates per mile
  - Flatbed rates per mile
  - Total cost estimates for specific lanes

- **LTL Spot Rates** by lane
  - Per CWT (hundredweight) pricing
  - Minimum charges
  - Fuel surcharges
  - Accessorial costs

#### Geographic Granularity Required:
- Top 100 metro areas
- Top 500 lane pairs (e.g., LA-Chicago, Dallas-Atlanta)
- Regional averages (Southeast, Midwest, West, Northeast, Southwest)

#### Creative Data Acquisition Strategies:

**Option 1: Public Load Board Scraping (Legal Gray Area - Assess ToS)**
- DAT public search pages (limited results without login)
- Truckstop.com public snippets
- FreightWaves SONAR market updates (free tier)
- Monitor for publicly shared rate information

**Option 2: Freight Matching Platform APIs (Freemium Models)**
- Convoy API (may have free tier for basic data)
- Uber Freight API (limited public endpoints)
- Transfix platform data
- Check for developer/sandbox accounts

**Option 3: Crowdsourced Intelligence**
- Build data sharing community (carriers/brokers submit anonymized rates)
- Reciprocal data exchange model
- Partner with small carriers for real transaction data
- Industry forums scraping (TruckersReport, uShip forums)

**Option 4: Public Rate Filings & Contracts**
- Government procurement sites (USASpending.gov - federal freight contracts)
- State DOT bid results (public contracts often include rates)
- FOIA requests for government freight spending

**Option 5: Financial Disclosures & Earnings Calls**
- Parse publicly traded carrier earnings (rate per mile disclosures)
- Broker quarterly reports (C.H. Robinson, XPO, etc.)
- Industry association reports (ATA, TIA public data)

**Option 6: Build Strategic Partnerships**
- Partner with TMS providers for anonymized data feeds
- University research partnerships (academic data access)
- Industry association membership for benchmark reports

**Option 7: Weather + Demand Correlation Model**
- Use public weather data, retail sales data, industrial production
- Build predictive model for rate movements
- Validate against limited real rate samples

---

### 2. **CONTRACT LANE PRICING** (Currently: None ❌)

#### What's Needed:
- Historical contract rates by lane
- Contract vs spot rate differentials
- Contract renewal trends
- Bid/RFP outcome data

#### Creative Acquisition:
- **Public Company Contracts**: Government contracts via FOIA/public procurement
- **Benchmark Reports**: Industry association surveys (often free to members)
- **RFP Databases**: Monitor public RFP postings (state governments, universities)
- **Carrier Partnerships**: Direct data sharing agreements
- **Shipper Community**: Build shipper network for bid result sharing

---

### 3. **CAPACITY INDICATORS** (Currently: None ❌)

#### What's Needed:
- Load-to-truck ratios by lane/region
- Tender rejection rates
- Equipment availability (van/reefer/flatbed)
- Days to cover metrics

#### Creative Acquisition:
- **FreightWaves SONAR**: Has free/trial data access
- **FMCSA Data**: Carrier authority filings (public), track new carrier registrations
- **Truck Counts**: DOT weigh station data (some states publish)
- **Job Postings**: Indeed/LinkedIn driver job postings as capacity proxy
- **Bankruptcy Filings**: Public PACER data for carrier failures
- **Parking Lot Monitoring**: Satellite imagery analysis of truck stops (experimental)

---

### 4. **LTL MARKET DATA** (Currently: None ❌)

#### What's Needed:
- LTL carrier rate cards (base rates + discounts)
- Transit times by lane
- Service level performance
- Minimum charge trends
- Dimensional weight policies

#### Creative Acquisition:
- **Published Tariffs**: Many LTL carriers publish base tariffs (SMC3, NMFC)
- **SMC3 Czar Lite**: Free/low-cost LTL rate benchmarking tool
- **Carrier Websites**: Scrape instant quote tools (FedEx Freight, XPO, Estes)
- **Industry Surveys**: NASSTRAC, CSCMP publish member benchmarks
- **Bill of Lading Data**: Some shippers may share anonymized BOL data

---

### 5. **MACRO FREIGHT INDICATORS** (Currently: Fake Data ❌)

#### What's Needed (Replace Synthetic Data):
- **Cass Freight Index** - Shipments & Expenditures
- **ATA Truck Tonnage Index**
- **FTR Trucking Conditions Index**
- **DAT Freight Index**
- **Outbound Tender Volume/Rejection Index** (OTVI/OTRI)

#### Creative Acquisition:
- **Cass Info**: Publishes monthly reports FREE on website
- **ATA**: Monthly press releases with index data FREE
- **FTR**: Summary data in press releases FREE (full report paid)
- **FreightWaves**: OTVI/OTRI trends in free articles
- **ACT Research**: Summary data in newsletters
- **Morgan Stanley/Bank Research**: Freight sector reports (if accessible)

**Action Item**: Replace all synthetic macro data with scraped press releases and free reports.

---

### 6. **GEOGRAPHIC & LANE INTELLIGENCE** (Currently: None ❌)

#### What's Needed:
- Top freight lanes ranked by volume
- Origin-Destination (O-D) pair pricing
- Regional rate differentials
- Port/metro-specific data

#### Creative Acquisition:
- **BTS (Bureau of Transportation Statistics)**: Freight Analysis Framework (FAF) - FREE
- **Census Bureau**: Commodity Flow Survey - FREE
- **State DOT Data**: Many states publish freight flow studies
- **Port Authority Reports**: LA/Long Beach, Savannah, etc. publish FREE data
- **Railroad Public Disclosures**: STB (Surface Transportation Board) data
- **Truck GPS Data**: Partner with ELD providers or use public traffic datasets

---

### 7. **FUEL SURCHARGE INTELLIGENCE** (Partially Covered ✓)

#### Current Status:
- ✅ Have diesel prices (EIA)
- ❌ Missing: FSC calculation methodologies, regional fuel price differentials

#### Enhancement Needed:
- Regional diesel prices (not just national)
- Carrier-specific FSC tables (many carriers publish)
- FSC lag analysis (comparing current price vs FSC application delay)

#### Creative Acquisition:
- **EIA State-Level Data**: Already free, add granularity
- **GasBuddy API**: Real-time fuel prices by location
- **Carrier Websites**: Scrape published FSC schedules (YRC, XPO, etc.)

---

### 8. **MARKET CONDITIONS & SENTIMENT** (Partially Covered ✓)

#### Current Status:
- ✅ News RSS feeds provide context
- ❌ Missing: Structured sentiment analysis, leading indicators

#### Enhancement Needed:
- Sentiment scoring of news articles
- Economic indicator correlation (PMI, retail sales, housing starts)
- Seasonal demand pattern recognition
- Peak season forecasting

#### Creative Acquisition:
- **Economic Data**: FRED (Federal Reserve) API - FREE
- **PMI Data**: ISM publishes monthly - FREE summary
- **Retail Sales**: Census Bureau - FREE
- **NLP Sentiment Analysis**: Open-source tools on existing news feeds
- **Google Trends**: Freight-related search volume as demand proxy

---

## Priority Data Gaps Ranked by Actionability

### **TIER 1 - Critical for Basic Functionality** (Implement Immediately)
1. **Real Spot Rate Data** (TL lanes) - Replace synthetic data
2. **Real Macro Indices** - Free sources available, scrape press releases
3. **Geographic/Lane Data** - BTS FAF data (free government source)
4. **LTL Rate Intelligence** - SMC3/carrier quote scraping

### **TIER 2 - Competitive Differentiation** (Implement Next)
5. **Capacity Indicators** - Load-to-truck ratios, rejection rates
6. **Contract Rate Benchmarks** - Government contracts, industry surveys
7. **Regional Fuel Pricing** - State-level diesel data
8. **Sentiment Analysis** - NLP on existing news feeds

### **TIER 3 - Advanced Features** (Future Roadmap)
9. **Predictive Analytics** - Rate forecasting models
10. **Real-time Capacity** - Equipment availability by location
11. **Carrier Performance** - On-time %, claims rates
12. **Economic Correlation** - Leading indicator dashboards

---

## Recommended Immediate Actions

### 🚨 **Remove All Synthetic Data**
**Files to Modify:**
- `backend/src/ingest/daily.ts:76-115` - Delete synthetic spot rate generation
- `backend/src/ingest/macro.ts:16-57` - Delete synthetic macro generation

**Replacement Strategy:**
1. Implement real Cass/ATA/FTR scrapers from free press releases
2. Implement lane-based spot rate tracking (start with top 50 lanes)
3. Add "Data Unavailable" states rather than showing fake data

---

### 📊 **Implement Free Real Data Sources** (Week 1-2)

#### Macro Indices (Replace Fake Data):
```
Sources:
- Cass Freight Index: https://www.cassinfo.com/freight-audit-indexes
- ATA Tonnage: https://www.trucking.org/news-insights/ata-truck-tonnage-index
- DAT Freight Index: https://www.dat.com/industry-trends/trendlines
- FreightWaves SONAR summaries: https://www.freightwaves.com/news/sonar
```

#### Geographic Data:
```
Sources:
- BTS Freight Analysis Framework: https://www.bts.gov/faf
- FMCSA Safety & Fitness Data: https://safer.fmcsa.dot.gov/
- State freight plans (TX, CA, FL DOTs)
```

#### Economic Indicators:
```
Sources:
- FRED API: https://fred.stlouisfed.org/docs/api/
- ISM Manufacturing PMI: https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/
- Census Retail Sales: https://www.census.gov/retail/index.html
```

---

### 🔍 **Implement Lane-Based Rate Tracking** (Week 3-4)

**Approach:**
1. Identify top 50 freight lanes by volume (use BTS FAF data)
2. Build scrapers for public rate indicators:
   - Government contract awards
   - Carrier instant quote tools (where ToS allows)
   - Industry benchmark reports
3. Implement manual rate input capability (for user-contributed data)
4. Add confidence scores to each rate data point

**Top Priority Lanes** (based on typical volume):
- LA/Long Beach → Chicago
- Chicago → Atlanta
- Dallas → Los Angeles
- Atlanta → NYC/NJ
- Houston → Dallas
- LA → Phoenix
- Chicago → Columbus, OH
- Atlanta → Miami
- Charlotte → Philadelphia
- Memphis → Chicago

---

### 💡 **Creative Data Acquisition Projects**

#### Project 1: Government Contract Intelligence
- Scrape USASpending.gov for federal freight contracts
- Parse state procurement sites (TX, CA, FL, NY)
- Build contract rate database from public awards

#### Project 2: Carrier Quote Aggregator
- Build quote request bot for LTL carriers with public tools
- Sample rates weekly for top lanes
- Track rate movement trends

#### Project 3: Crowdsourced Freight Network
- Create shipper/carrier data contribution program
- Incentivize anonymous rate sharing
- Build two-sided marketplace of intelligence

#### Project 4: Economic Correlation Engine
- Pull FRED economic data (ISM PMI, retail sales, industrial production)
- Correlate with freight rate movements
- Build predictive indicators

#### Project 5: Carrier Financial Health Tracker
- Scrape public carrier earnings reports
- Track bankruptcy filings (PACER)
- Monitor new authority filings (FMCSA)
- Build capacity trend predictions

---

## Data Source Reference Matrix

| Data Type | Free Sources | Paid Sources | Creative Alternatives |
|-----------|-------------|--------------|---------------------|
| **TL Spot Rates** | Limited DAT snippets, FreightWaves articles | DAT iQ, Truckstop.com, SONAR | Government contracts, carrier partnerships, crowdsourcing |
| **LTL Rates** | Carrier instant quotes, SMC3 Czar Lite | SMC3 Bid Matrix, 3PL systems | Tariff scraping, shipper surveys, BOL data |
| **Macro Indices** | Cass (free), ATA (free), DAT summaries | FTR full reports, ACT Research | Press release scraping, financial disclosures |
| **Capacity Data** | FMCSA registrations, job postings | SONAR, FourKites, project44 | Bankruptcy filings, parking lot satellite imagery |
| **Lane Intelligence** | BTS FAF, state DOT reports | Proprietary freight flow data | Traffic data, port reports, Census data |
| **Fuel Prices** | EIA (free), GasBuddy | OPIS | Regional scraping, truck stop APIs |
| **Economic Indicators** | FRED (free), Census (free), ISM (free) | Premium research services | Google Trends, sentiment analysis |

---

## Technical Implementation Priorities

### Phase 1: Data Integrity (Immediate)
- [ ] Remove all synthetic data generation
- [ ] Implement Cass Index scraper (free press releases)
- [ ] Implement ATA Tonnage scraper (free press releases)
- [ ] Add DAT Trendlines scraper (free public data)
- [ ] Implement FRED API for economic indicators
- [ ] Add data source attribution to all metrics

### Phase 2: Geographic Expansion (Week 2-4)
- [ ] Integrate BTS FAF data for lane identification
- [ ] Add top 50 lane tracking framework
- [ ] Implement regional fuel price tracking (state-level EIA)
- [ ] Add metro area definitions and mapping

### Phase 3: LTL Coverage (Week 4-6)
- [ ] Build LTL carrier quote scrapers (FedEx Freight, XPO, Estes)
- [ ] Integrate SMC3 data (if accessible)
- [ ] Add LTL-specific metrics (CWT pricing, transit times)
- [ ] Implement service level tracking

### Phase 4: Capacity Intelligence (Week 6-8)
- [ ] FMCSA new authority tracker
- [ ] Carrier bankruptcy monitor (PACER integration)
- [ ] Job posting volume tracker (driver demand proxy)
- [ ] Build capacity tightness indicators

### Phase 5: Contract Intelligence (Week 8-10)
- [ ] Government contract scraper (USASpending.gov)
- [ ] State procurement monitor
- [ ] Build spot-to-contract rate differential analysis
- [ ] Add RFP outcome tracking

### Phase 6: Predictive Analytics (Week 10-12)
- [ ] Economic correlation models
- [ ] Seasonal pattern recognition
- [ ] Rate forecasting (basic ML models)
- [ ] Anomaly detection for rate spikes

---

## Measurement of Actionable Intelligence

**Current Platform Score: 1/10**
- Has news context (+1)
- All rate data is fake (-5)
- No geographic granularity (-2)
- No capacity indicators (-2)

**Target Platform Score: 8-9/10**

### Success Metrics for Actionable Intelligence:
1. **Decision Confidence**: Can user make spot/contract procurement decision based on data?
2. **Data Freshness**: Is data <24hrs old for daily metrics, <1 week for macro?
3. **Geographic Relevance**: Does user see their specific lanes?
4. **Predictive Value**: Can user anticipate rate movements?
5. **Cost Savings**: Can user save 5-10% on freight spend using platform insights?

---

## Budget Considerations

### Zero-Cost Approach (Maximum Creative Solutions):
- All data from free government sources, press releases, public filings
- Web scraping within legal/ToS boundaries
- Crowdsourced user-contributed data
- Economic correlation as rate proxy
- **Limitation**: Less granular, delayed data, limited coverage

### Minimal Budget Approach ($100-500/mo):
- SMC3 Czar Lite subscription (~$200/mo)
- FreightWaves SONAR trial/starter tier
- Premium API access for select data
- **Benefit**: Significantly better data quality, real-time elements

### Full Intelligence Platform ($2K-10K/mo):
- DAT iQ subscription
- SONAR Professional
- SMC3 Bid Matrix
- Carrier performance data feeds
- **Benefit**: Institutional-grade intelligence, competitive with major 3PLs

---

## Competitive Landscape Analysis

### Free/Open Data Platforms (Competitive Set):
- **FreightWaves Public Dashboard**: Limited free data
- **DAT Trendlines**: Summary charts, no raw data
- **ATA Monthly Reports**: Macro only
- **BTS FAF**: Geographic, no pricing

### Differentiation Opportunity:
**"Best free freight intelligence platform"** by aggregating all available public data sources into single actionable dashboard with:
1. Real data only (no synthetic)
2. Lane-specific insights (not just national)
3. Spot + Contract intelligence
4. TL + LTL coverage
5. Economic leading indicators
6. Predictive analytics

---

## Risk Assessment

### Legal/ToS Risks:
- **Web Scraping**: Review ToS for each source, use public data only
- **Data Republishing**: Ensure proper attribution, respect copyright
- **API Limits**: Stay within free tier limits or upgrade

### Data Quality Risks:
- **Free Data Limitations**: Less frequent updates, less granular
- **Crowdsourced Data**: Requires validation, potential gaming
- **Economic Proxies**: Correlation ≠ causation

### Mitigation:
- Clear data source attribution
- Confidence scores on all metrics
- Multiple data sources for validation
- Transparent methodology documentation

---

## Conclusion

**Current State**: Platform is 95% synthetic data with minimal actionable value.

**Required Transformation**:
1. **Immediate**: Remove all fake data, implement free real data sources
2. **Short-term**: Add geographic/lane granularity, LTL coverage
3. **Medium-term**: Build capacity indicators, contract intelligence
4. **Long-term**: Predictive analytics, full market coverage

**Guiding Principle**: **"Real data or no data"** - Never show synthetic/fake information. Better to show "Data Unavailable" than misleading fake trends.

**Actionable Intelligence Test**: Before adding any feature, ask:
- "Can a freight broker make a better buy/sell decision with this data?"
- "Can a shipper negotiate better rates with this intelligence?"
- "Would I trust my money on this data?"

If answer is "no" - don't ship it.
