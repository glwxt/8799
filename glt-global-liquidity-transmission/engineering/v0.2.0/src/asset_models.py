"""GLT V1.0 asset-factor contracts, NOT invented numeric scoring formulas."""
FACTORS={
 'BTC-GT':['global_usd','dxy','us_10y_real','btc_etf_primary_net_flow','spot_demand','funding_rate','open_interest','liquidations','stablecoin_supply'],
 'GOLD-GT':['us_10y_real','dxy','gold_etf_primary_flow','central_bank_gold_purchases','safe_haven_demand','physical_gold_demand'],
 'EQUITY-GT':['us_10y_real','us_10y_nominal','dxy','earnings_forecasts','valuation','market_breadth','us_equity_primary_flow','regional_foreign_flows']
}
def model_status():
 return {key:{'score':None,'direction':None,'status':'待权重/方向函数/标定批准，不产生评分','required_factors':v} for key,v in FACTORS.items()}
