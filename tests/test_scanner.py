import unittest
from scanner.header_analysis import evaluate as evaluate_headers
from scanner.cookie_analysis import evaluate as evaluate_cookies
from scanner.cms_detection import evaluate as evaluate_cms
from scanner.utils import calculate_grade, is_safe_target

class TestVulTureScanner(unittest.TestCase):
    def test_calculate_grade(self):
        self.assertEqual(calculate_grade(95), "A")
        self.assertEqual(calculate_grade(85), "B")
        self.assertEqual(calculate_grade(75), "C")
        self.assertEqual(calculate_grade(65), "D")
        self.assertEqual(calculate_grade(40), "F")

    def test_ssrf_protection(self):
        self.assertFalse(is_safe_target("localhost"))
        self.assertFalse(is_safe_target("127.0.0.1"))
        self.assertFalse(is_safe_target("192.168.1.1"))
        self.assertFalse(is_safe_target("10.0.0.1"))
        self.assertFalse(is_safe_target("169.254.169.254"))
        self.assertFalse(is_safe_target("::1"))
        self.assertTrue(is_safe_target("example.com"))

    def test_header_analysis(self):
        headers = {
            "Content-Security-Policy": "default-src 'self'",
            "Strict-Transport-Security": "max-age=31536000",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff"
        }
        res = evaluate_headers(headers)
        self.assertTrue(res["details"]["csp"])
        self.assertTrue(res["details"]["hsts"])
        self.assertTrue(res["details"]["x_frame_options"])
        self.assertTrue(res["details"]["x_content_type_options"])
        self.assertFalse(res["details"]["referrer_policy"])

    def test_cookie_analysis(self):
        raw_cookies = [
            "session_id=abc123xyz; Path=/; Secure; HttpOnly; SameSite=Strict",
            "tracker=456; Path=/"
        ]
        res = evaluate_cookies(raw_cookies)
        self.assertTrue(res["has_cookies"])
        self.assertEqual(len(res["cookies"]), 2)
        self.assertTrue(res["cookies"][0]["secure"])
        self.assertTrue(res["cookies"][0]["httponly"])
        self.assertFalse(res["cookies"][1]["secure"])
        self.assertGreaterEqual(len(res["issues"]), 2)

    def test_cms_and_tech_detection(self):
        html = """
        <html>
          <head>
            <meta name="generator" content="WordPress 6.4.2" />
          </head>
          <body>
            <div id="__next">Hello NextJS</div>
          </body>
        </html>
        """
        headers = {
            "server": "nginx/1.24.0",
            "x-powered-by": "PHP/8.2"
        }
        res = evaluate_cms(html, headers)
        findings = res["findings"]
        techs = [t["name"] for t in res["technologies"]]
        self.assertTrue(any("nginx" in t.lower() for t in techs))
        self.assertTrue(any("next.js" in t.lower() for t in techs))
        self.assertTrue(any("wordpress" in t.lower() for t in techs))
        self.assertTrue(any("Information Disclosure" in f for f in findings))

if __name__ == "__main__":
    unittest.main()
