const Home = () => {
  return (
    <div>
      {/* Hero Section */}
      <section id="home" className="section-padding bg-gradient-to-br from-light to-light-100 dark:from-dark-900 dark:to-dark-800">
        <div className="container-custom">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-dark-800 dark:text-white mb-6 animation-init animate-slide-in-left">
                Smart Investing Made <span className="text-primary">Simple</span>
              </h1>
              <p className="text-body-lg text-dark-700 dark:text-light-300 mb-8 animation-init animate-slide-in-left animate-delay-200">
                Lumia is your intelligent roboadvisor platform that leverages advanced data analytics 
                and machine learning to provide personalized investment strategies tailored to your 
                financial goals.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 animation-init animate-slide-in-left animate-delay-300">
                <button className="btn-primary">Start Investing</button>
                <button className="btn-outline">Learn More</button>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-6 mt-12">
                <div className="animation-init animate-slide-up animate-delay-400">
                  <h3 className="text-primary mb-2">$2B+</h3>
                  <p className="text-body-sm text-dark-700 dark:text-light-300">Assets Managed</p>
                </div>
                <div className="animation-init animate-slide-up animate-delay-500">
                  <h3 className="text-primary mb-2">50K+</h3>
                  <p className="text-body-sm text-dark-700 dark:text-light-300">Active Users</p>
                </div>
                <div className="animation-init animate-slide-up animate-delay-600">
                  <h3 className="text-primary mb-2">98%</h3>
                  <p className="text-body-sm text-dark-700 dark:text-light-300">Satisfaction Rate</p>
                </div>
              </div>
            </div>

            <div className="relative animation-init animate-slide-in-right animate-delay-300">
              <div className="card dark:bg-dark-800 dark:border-dark-700 animate-float">
                <div className="aspect-video gradient-primary rounded-lg flex items-center justify-center">
                  <svg className="w-32 h-32 text-white animate-pulse-slow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Us Section */}
      <section id="about" className="section-padding bg-white dark:bg-dark-900">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-dark-800 dark:text-white mb-4">About Lumia</h2>
            <p className="text-body-lg text-dark-700 dark:text-light-300 max-w-3xl mx-auto">
              We're revolutionizing the investment advisory industry through technology, 
              data science, and a commitment to democratizing wealth management.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Mission */}
            <div className="card dark:bg-dark-800 dark:border-dark-700">
              <div className="w-14 h-14 bg-primary-light rounded-lg flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-primary-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h4 className="text-dark-800 dark:text-white mb-3">Our Mission</h4>
              <p className="text-dark-700 dark:text-light-300">
                To make sophisticated investment strategies accessible to everyone through 
                cutting-edge technology and personalized guidance.
              </p>
            </div>

            {/* Vision */}
            <div className="card dark:bg-dark-800 dark:border-dark-700">
              <div className="w-14 h-14 bg-secondary-light rounded-lg flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-secondary-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <h4 className="text-dark-800 dark:text-white mb-3">Our Vision</h4>
              <p className="text-dark-700 dark:text-light-300">
                To become the world's most trusted roboadvisor platform, empowering millions 
                to achieve their financial dreams with confidence.
              </p>
            </div>

            {/* Values */}
            <div className="card dark:bg-dark-800 dark:border-dark-700">
              <div className="w-14 h-14 bg-primary-light rounded-lg flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-primary-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h4 className="text-dark-800 dark:text-white mb-3">Our Values</h4>
              <p className="text-dark-700 dark:text-light-300">
                Transparency, security, innovation, and client-first approach guide 
                everything we do at Lumia.
              </p>
            </div>
          </div>

          {/* What We Do */}
          <div className="mt-20">
            <h3 className="text-dark-800 dark:text-white text-center mb-12">What We Do</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">1</span>
                  </div>
                </div>
                <div>
                  <h5 className="text-dark-800 dark:text-white mb-2">Personalized Portfolio Management</h5>
                  <p className="text-dark-700 dark:text-light-300">
                    We create customized investment portfolios based on your risk tolerance, 
                    financial goals, and time horizon using advanced algorithms.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">2</span>
                  </div>
                </div>
                <div>
                  <h5 className="text-dark-800 dark:text-white mb-2">Real-Time Market Analysis</h5>
                  <p className="text-dark-700 dark:text-light-300">
                    Our platform continuously monitors market conditions and adjusts your 
                    portfolio to optimize returns and manage risk.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">3</span>
                  </div>
                </div>
                <div>
                  <h5 className="text-dark-800 dark:text-white mb-2">Data-Driven Insights</h5>
                  <p className="text-dark-700 dark:text-light-300">
                    Leveraging big data and machine learning to identify opportunities and 
                    trends that traditional advisors might miss.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">4</span>
                  </div>
                </div>
                <div>
                  <h5 className="text-dark-800 dark:text-white mb-2">Tax Optimization</h5>
                  <p className="text-dark-700 dark:text-light-300">
                    Smart tax-loss harvesting and strategic rebalancing to maximize your 
                    after-tax returns.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="section-padding bg-light-100 dark:bg-dark-800 transition-colors duration-300">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-dark-800 dark:text-white mb-4">How Lumia Works</h2>
            <p className="text-body-lg text-dark-700 dark:text-light-300 max-w-3xl mx-auto">
              Our platform combines cutting-edge technology with financial expertise to 
              deliver superior investment outcomes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="card dark:bg-dark-800 dark:border-dark-700">
                <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <h5 className="text-dark-800 dark:text-white mb-3">Create Profile</h5>
                <p className="text-body-sm text-dark-700 dark:text-light-300">
                  Tell us about your financial goals, risk tolerance, and investment timeline.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="card dark:bg-dark-800 dark:border-dark-700">
                <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h5 className="text-dark-800 dark:text-white mb-3">AI Analysis</h5>
                <p className="text-body-sm text-dark-700 dark:text-light-300">
                  Our AI algorithms analyze market data and create a personalized strategy for you.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="card dark:bg-dark-800 dark:border-dark-700">
                <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h5 className="text-dark-800 dark:text-white mb-3">Start Investing</h5>
                <p className="text-body-sm text-dark-700 dark:text-light-300">
                  Fund your account and we'll automatically build and manage your portfolio.
                </p>
              </div>
            </div>

            {/* Step 4 */}
            <div className="text-center">
              <div className="card dark:bg-dark-800 dark:border-dark-700">
                <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <h5 className="text-dark-800 dark:text-white mb-3">Track Growth</h5>
                <p className="text-body-sm text-dark-700 dark:text-light-300">
                  Monitor your portfolio's performance with real-time updates and insights.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Data Collection Section */}
      <section className="section-padding bg-white dark:bg-dark-900 transition-colors duration-300">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-dark-800 dark:text-white mb-4">How We Collect & Use Data</h2>
            <p className="text-body-lg text-dark-700 dark:text-light-300 max-w-3xl mx-auto">
              Transparency is at the core of our platform. Here's how we gather and utilize 
              data to provide you with the best investment experience.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="space-y-6">
                <div className="flex gap-4 items-start">
                  <div className="w-10 h-10 bg-primary-light rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-6 h-6 text-primary-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                    </svg>
                  </div>
                  <div>
                    <h5 className="text-dark-800 dark:text-white mb-2">Market Data Integration</h5>
                    <p className="text-dark-700 dark:text-light-300">
                      We collect real-time market data from multiple exchanges, including stocks, 
                      ETFs, mutual funds, and cryptocurrencies, updated every second.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="w-10 h-10 bg-secondary-light rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-6 h-6 text-secondary-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                  </div>
                  <div>
                    <h5 className="text-dark-800 dark:text-white mb-2">News & Sentiment Analysis</h5>
                    <p className="text-dark-700 dark:text-light-300">
                      Our AI scans thousands of financial news sources daily, analyzing sentiment 
                      to identify market trends and potential opportunities.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="w-10 h-10 bg-primary-light rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-6 h-6 text-primary-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <h5 className="text-dark-800 dark:text-white mb-2">Fundamental Analysis</h5>
                    <p className="text-dark-700 dark:text-light-300">
                      We gather company financials, earnings reports, and economic indicators 
                      to perform comprehensive fundamental analysis.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="w-10 h-10 bg-secondary-light rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-6 h-6 text-secondary-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <div>
                    <h5 className="text-dark-800 dark:text-white mb-2">Privacy & Security</h5>
                    <p className="text-dark-700 dark:text-light-300">
                      All data is encrypted end-to-end, and we never share your personal information 
                      with third parties. Your privacy is our priority.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="card dark:bg-dark-800 dark:border-dark-700 bg-gradient-to-br from-primary-light to-secondary-light">
              <div className="p-8">
                <h4 className="text-dark-800 dark:text-white mb-6">Data Sources</h4>
                <ul className="space-y-3 list-none p-0">
                  <li className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    <span className="text-dark-700 dark:text-light-300">NSE, BSE, NYSE, NASDAQ</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    <span className="text-dark-700 dark:text-light-300">Indian Mutual Funds (AMFI)</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    <span className="text-dark-700 dark:text-light-300">Cryptocurrency Exchanges</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    <span className="text-dark-700 dark:text-light-300">Financial News APIs</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    <span className="text-dark-700 dark:text-light-300">Economic Indicators</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    <span className="text-dark-700 dark:text-light-300">Company Fundamentals</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="section-padding bg-dark-800 text-light">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-white mb-4">Our Services</h2>
            <p className="text-body-lg text-light-300 max-w-3xl mx-auto">
              Comprehensive investment solutions designed to help you achieve your financial goals.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-dark-700 rounded-xl p-6 hover:bg-dark-800 transition-colors border border-dark-700 hover:border-primary">
              <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h5 className="text-white mb-3">Automated Investing</h5>
              <p className="text-light-300">
                Set it and forget it. Our algorithms handle everything from portfolio construction 
                to rebalancing.
              </p>
            </div>

            <div className="bg-dark-700 rounded-xl p-6 hover:bg-dark-800 transition-colors border border-dark-700 hover:border-primary">
              <div className="w-12 h-12 bg-secondary rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <h5 className="text-white mb-3">Tax Optimization</h5>
              <p className="text-light-300">
                Maximize returns with intelligent tax-loss harvesting and strategic asset location.
              </p>
            </div>

            <div className="bg-dark-700 rounded-xl p-6 hover:bg-dark-800 transition-colors border border-dark-700 hover:border-primary">
              <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
              </div>
              <h5 className="text-white mb-3">Portfolio Analytics</h5>
              <p className="text-light-300">
                Detailed insights into your portfolio performance, risk metrics, and asset allocation.
              </p>
            </div>

            <div className="bg-dark-700 rounded-xl p-6 hover:bg-dark-800 transition-colors border border-dark-700 hover:border-primary">
              <div className="w-12 h-12 bg-secondary rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
                </svg>
              </div>
              <h5 className="text-white mb-3">Goal Planning</h5>
              <p className="text-light-300">
                Set financial goals and we'll create a personalized roadmap to achieve them.
              </p>
            </div>

            <div className="bg-dark-700 rounded-xl p-6 hover:bg-dark-800 transition-colors border border-dark-700 hover:border-primary">
              <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </div>
              <h5 className="text-white mb-3">Smart Alerts</h5>
              <p className="text-light-300">
                Stay informed with personalized notifications about your portfolio and market opportunities.
              </p>
            </div>

            <div className="bg-dark-700 rounded-xl p-6 hover:bg-dark-800 transition-colors border border-dark-700 hover:border-primary">
              <div className="w-12 h-12 bg-secondary rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <h5 className="text-white mb-3">24/7 Support</h5>
              <p className="text-light-300">
                Expert support team available round the clock to assist you with any questions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="contact" className="section-padding bg-gradient-to-br from-primary to-secondary">
        <div className="container-custom text-center">
          <h2 className="text-white mb-6">Ready to Start Your Investment Journey?</h2>
          <p className="text-body-lg text-dark-700 dark:text-light-300 mb-8 max-w-2xl mx-auto">
            Join thousands of investors who trust Lumia to manage their wealth intelligently.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white dark:bg-dark-900 text-primary hover:bg-light-100 dark:hover:bg-dark-800 font-semibold py-3 px-8 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl">
              Get Started Free
            </button>
            <button className="bg-transparent border-2 border-white text-white hover:bg-white hover:dark:bg-dark-800 hover:text-primary font-semibold py-3 px-8 rounded-lg transition-all duration-200">
              Schedule a Demo
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;









