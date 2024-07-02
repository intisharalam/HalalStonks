'use client'

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styles from '../../styles/dashboard.module.scss';
import SearchBar from '../../components/searchbar';
import Card from '../../components/card';
import LineChart from '../../components/linechart';
import Watchlist from '../../components/watchlist';
import BarChart from '../../components/barchart';
import CriteriaTable from '../../components/criteriatable';
import { useRouter } from 'next/navigation';


export default function Dashboard() {
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [companyData, setCompanyData] = useState({});
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      if (router.query && router.query.symbol) {
        const { symbol } = router.query;
        setSelectedSymbol(symbol);
        await fetchCompanyData(symbol);
      }
    };
  
    // Call fetchData when router.query.symbol exists and changes
    if (router.query && router.query.symbol) {
      fetchData();
    }
  }, [router.query]); // Dependency on router.query ensures it runs when query changes

  const fetchCompanyData = async (symbol) => {
    setLoading(true);
    try {
      const companyResponse = await axios.post('https://halal-stonks-backend.vercel.app/api/get_company_data', { symbol });
      const companyData = companyResponse.data;
      setCompanyData(companyData);
      /*console.log(companyData.data['Halal Score'])*/
    } catch (error) {
      console.error('Error fetching data:', error);
      setCompanyData({}); // Optionally, handle error state
    } finally {
      setLoading(false);
    }
  };

  const handleSymbolSelect = async (symbol) => {
    setSelectedSymbol(symbol);
    await fetchCompanyData(symbol);
    router.push(`/dashboard?symbol=${symbol}`);
  };

  const computeBenjaminGrahamCriteria = (data) => {
    const criteriaAnalysis = [];
  
    // Market Capitalisation
    const marketCap = data.data && data.data['Market Cap'];
    if (marketCap !== 'N/A' && parseFloat(marketCap) > 2) {
      criteriaAnalysis.push({ criteria: 'Market Capitalisation', limit: '> $2B', result: 'Y' });
    } else {
      criteriaAnalysis.push({ criteria: 'Market Capitalisation', limit: '> $2B', result: marketCap !== 'N/A' ? 'N' : '---' });
    }
  
    // Liquidity Ratio
    const liquidityRatio = data.data && data.data['Liquidity Ratio'];
    if (liquidityRatio !== 'N/A' && parseFloat(liquidityRatio) > 2) {
      criteriaAnalysis.push({ criteria: 'Liquidity Ratio', limit: '>2', result: 'Y' });
    } else {
      criteriaAnalysis.push({ criteria: 'Liquidity Ratio', limit: '>2', result: liquidityRatio !== 'N/A' ? 'N' : '---' });
    }
  
    // Earnings Consistency
    const earningsConsistency = data.data && data.data['Earnings Consistency'];
    if (earningsConsistency === 'Positive') {
      criteriaAnalysis.push({ criteria: 'Earnings Consistency', limit: 'No negative earnings*', result: 'Y' });
    } else {
      criteriaAnalysis.push({ criteria: 'Earnings Consistency', limit: 'No negative earnings*', result: 'N' || '---' });
    }
  
    // Dividend History (assuming `Uninterrupted Dividends` is a boolean in your data)
    const uninterruptedDividends = data.data && data.data['Uninterrupted Dividends'];
    if (uninterruptedDividends) {
      criteriaAnalysis.push({ criteria: 'Dividend History', limit: 'Uninterrupted dividends*', result: 'Y' });
    } else {
      criteriaAnalysis.push({ criteria: 'Dividend History', limit: 'Uninterrupted dividends*', result: 'N' !== undefined ? 'N' : '---' });
    }
  
    // Earnings Growth Rate
    const earningsGrowthRate = data.data && data.data['Earnings Growth Rate'];
    if (earningsGrowthRate && parseFloat(earningsGrowthRate) > 33) {
      criteriaAnalysis.push({ criteria: 'Earnings Growth Rate', limit: 'At least 33% increase*', result: `Y` });
    } else {
      criteriaAnalysis.push({ criteria: 'Earnings Growth Rate', limit: 'At least 33% increase*', result: earningsGrowthRate !== undefined ? 'N' : '---' });
    }
  
    // Price to Earnings Ratio (P/E)
    const peRatio = data.data && data.data['P/E Ratio'];
    if (peRatio !== 'N/A' && parseFloat(peRatio) < 15) {
      criteriaAnalysis.push({ criteria: 'Price to Earnings Ratio (P/E)', limit: '< 15', result: 'Y' });
    } else {
      criteriaAnalysis.push({ criteria: 'Price to Earnings Ratio (P/E)', limit: '< 15', result: peRatio !== 'N/A' ? 'N' : '---' });
    }
  
    // Price to Book Ratio (P/B)
    const pbRatio = data.data && data.data['Price to Book Ratio'];
    if (pbRatio !== 'N/A' && parseFloat(pbRatio) < 1.5) {
      criteriaAnalysis.push({ criteria: 'Price to Book Ratio (P/B)', limit: '< 1.5', result: 'Y' });
    } else {
      criteriaAnalysis.push({ criteria: 'Price to Book Ratio (P/B)', limit: '< 1.5', result: pbRatio !== 'N/A' ? 'N' : '---' });
    }
  
    // Debt to Equity Ratio (D/E)
    const debtToEquityRatio = data.data && data.data['Debt to Equity Ratio'];
    if (debtToEquityRatio !== 'N/A' && parseFloat(debtToEquityRatio) < 0.5) {
      criteriaAnalysis.push({ criteria: 'Debt to Equity Ratio (D/E)', limit: '<0.5', result: 'Y' });
    } else {
      criteriaAnalysis.push({ criteria: 'Debt to Equity Ratio (D/E)', limit: '<0.5', result: debtToEquityRatio !== 'N/A' ? 'N' : '---' });
    }
  
    return criteriaAnalysis;
  };
  
  const computeShariahCriteria = (data) => {
    const criteriaAnalysis = [];
    
    if (!data || !Array.isArray(data) || data.length !== 5) {
      // Handle case where data is not valid or not provided
      criteriaAnalysis.push(
        { criteria: 'Industry', limit: 'Not Haram*', result: '---' },
        { criteria: 'Haram Income', limit: '<5%', result: '---' },
        { criteria: 'Interest-Debt-to-Asset Ratio', limit: '<33%', result: '---' },
        { criteria: 'Illiquid Asset Ratio', limit: '>20%', result: '---' },
        { criteria: 'Net Liquid Asset to Market Cap', limit: '<Market Cap', result: '---' }
      );
    } else {
      // Example criteria based on boolean values
      criteriaAnalysis.push(
        { criteria: 'Industry', limit: 'Not Haram*', result: data[0] ? 'Y' : 'N' },
        { criteria: 'Haram Income', limit: '<5%', result: data[1] ? 'Y' : 'N' },
        { criteria: 'Interest-Debt-to-Asset Ratio', limit: '<33%', result: data[2] ? 'Y' : 'N' },
        { criteria: 'Illiquid Asset Ratio', limit: '>20%', result: data[3] ? 'Y' : 'N' },
        { criteria: 'Net Liquid Asset to Market Cap', limit: '<Market Cap', result: data[4] ? 'Y' : 'N' }
      );
    }
    
    return criteriaAnalysis;
  };
  
  

  return (
    <div className={styles.container}>
      <div className={styles.stockName}>
        <div className={styles.ticker}>
          {loading ? (
            'Loading...'
          ) : (
            <>
              <div className={styles.companyName}>
                {companyData.data && Object.keys(companyData.data).length > 0 ? (
                  `${companyData.data['Company Name']} (${companyData.data['Symbol']})`
                ) : (
                  '---'
                )}
              </div>
              <div className={styles.sector}>
                {companyData.data && Object.keys(companyData.data).length > 0 ? (
                  `Industry: ${companyData.data['Industry']}`
                ) : (
                  'Industry: ---'
                )}
              </div>
            </>
          )}
        </div>
        {/* Ensure SearchBar is correctly integrated */}
        <SearchBar
          className={styles.searchbar}
          onSelect={handleSymbolSelect}  // Pass handleSymbolSelect function to SearchBar's onSelect event
        />

      </div>

      <div className={styles.cardRow}>
        <Card
          topText="Halal Status"
          middleText={
            loading
              ? 'Loading...'
              : companyData.data && companyData.data['Halal Stock Criteria Results']
              ? !companyData.data['Halal Stock Criteria Results'][0]
                ? 'Disgrace'
                : companyData.data['Halal Score'] !== undefined
                ? companyData.data['Halal Score'] === 5
                  ? 'Strong'
                  : companyData.data['Halal Score'] === 4
                  ? 'Medium'
                  : companyData.data['Halal Score'] === 3
                  ? 'Weak'
                  : companyData.data['Halal Score'] === 2
                  ? 'Doubtful'
                  : 'Disgrace'
                : '---'
              : '---'
          }
          bottomText={
            loading
              ? 'Loading...'
              : companyData.data && companyData.data['Halal Score'] !== undefined
              ? `Score: ${companyData.data['Halal Score']}/5`
              : ''
          }
        />





        <Card
          topText="P/E ratio"
          middleText={loading ? 'Loading...' : (companyData.data ? companyData.data['P/E Ratio'] : '---')}
          bottomText={loading ? 'Loading...' : (`Dividend Yield: ${companyData.data ? companyData.data['Dividend Yield'] : '---'}`)}
        />
        <Card
          topText="Market Cap"
          middleText={loading ? 'Loading...' : (`${companyData.data ? companyData.data['Market Cap'] : '---'}`)}
          bottomText={loading ? 'Loading...' : (`Beta: ${companyData.data ? companyData.data['Beta'] : '---'}`)}
        />
      </div>
  
      <div className={styles.stockData}>
        <div className={styles.graph}>
          <LineChart chartData={loading ? [] : (companyData.data ? companyData.data['Close Prices'] : [{ time: '---', price: 0 },])} />
        </div>
        <div className={styles.watchlist}>
          <Watchlist />
        </div>
      </div>
  
      <div className={styles.financialData}>
        <div className={styles.benjaminCriteria}>
          <CriteriaTable
            criteriaData={computeBenjaminGrahamCriteria(companyData)}
            title="Benjamin Graham’s Criteria"
          />
        </div>
  
        <div className={styles.halalCriteria}>
          <CriteriaTable
            criteriaData={
              companyData.data && companyData.data['Halal Stock Criteria Results']
                ? computeShariahCriteria(companyData.data['Halal Stock Criteria Results'])
                : []
            }
            title="Sharia Law Criteria"
          />
        </div>

  
        <div className={styles.balanceSheets}>
          <BarChart chartData={loading ? [] : (companyData.data ? companyData.data['Assets&Liabilities'] : [{ year: '---', assets: 0, liabilities: 0 },])} />
        </div>
      </div>
    </div>
  );
  

}
