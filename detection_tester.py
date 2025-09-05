# detection_tester.py
from browser_engine import AdvancedBrowserEngine
import time

class DetectionTester:
    def __init__(self):
        self.test_sites = [
            "https://bot.sannysoft.com/",
            "https://arh.antoinevastel.com/bots/areyouheadless",
            "https://fingerprintjs.github.io/fingerprintjs/",
            "https://pixelscan.net/",
            "https://amiunique.org/fingerprint",
        ]
    
    def run_tests(self, num_tests=5):
        """Run tests against detection sites"""
        results = {}
        
        for i in range(num_tests):
            print(f"Running test {i+1}/{num_tests}")
            browser = AdvancedBrowserEngine(headless=True)
            
            try:
                page = browser.launch_stealth_browser()
                
                for site in self.test_sites:
                    print(f"Testing {site}")
                    page.goto(site)
                    time.sleep(5)  # Wait for tests to complete
                    
                    # Take screenshot for analysis
                    screenshot_path = f"test_results/test_{i+1}_{site.split('//')[1].replace('/', '_')}.png"
                    os.makedirs("test_results", exist_ok=True)
                    page.screenshot(path=screenshot_path)
                    
                    # Try to extract test results (site-specific)
                    result = self._extract_test_result(page, site)
                    if site not in results:
                        results[site] = []
                    results[site].append(result)
                
                browser.close()
                
            except Exception as e:
                print(f"Test {i+1} failed: {e}")
                browser.close()
        
        # Generate report
        self._generate_report(results)
        return results
    
    def _extract_test_result(self, page, site):
        """Extract test results based on the detection site"""
        if "sannysoft" in site:
            # Check for bot detection indicators
            try:
                content = page.content()
                if "failed" in content.lower():
                    return "Detected"
                elif "passed" in content.lower():
                    return "Passed"
            except:
                return "Error"
        
        elif "areyouheadless" in site:
            try:
                result = page.text_content("#headless")
                return "Headless" if "true" in result.lower() else "Not Headless"
            except:
                return "Error"
        
        # Add more site-specific extraction methods
        
        return "Unknown"
    
    def _generate_report(self, results):
        """Generate a comprehensive test report"""
        report = "=== STEALTH TEST REPORT ===\n\n"
        
        for site, site_results in results.items():
            report += f"Site: {site}\n"
            passed = site_results.count("Passed") + site_results.count("Not Headless")
            total = len(site_results)
            report += f"Success Rate: {passed}/{total} ({passed/total*100:.2f}%)\n"
            report += f"Results: {site_results}\n\n"
        
        # Save report
        with open("test_results/report.txt", "w") as f:
            f.write(report)
        
        print(report)