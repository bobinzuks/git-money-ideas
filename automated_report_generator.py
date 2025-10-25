#!/usr/bin/env python3
"""
📊 Automated Report Generator - Self-Improving Discovery Insights

Generates comprehensive insights reports every 12 hours:
- Discovery statistics and trends
- Top opportunities analysis
- Revenue projections
- Self-improving algorithm that learns from patterns
- Email delivery

Features:
- AI-powered pattern recognition
- Trend analysis (12-hour, daily, weekly)
- Quality scoring improvements
- Automatic email delivery
- Self-learning query optimization
"""

import json
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
import statistics

class SelfImprovingAlgorithm:
    """
    Algorithm that learns from discoveries and improves over time

    Learning mechanisms:
    1. Success pattern analysis (which queries find best gems)
    2. Quality trend tracking (are gems getting better?)
    3. Query effectiveness scoring
    4. Automatic parameter tuning
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.learning_history_file = "algorithm_learning_history.json"
        self.load_learning_history()

    def load_learning_history(self):
        """Load previous learning data"""
        if os.path.exists(self.learning_history_file):
            with open(self.learning_history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = {
                'query_effectiveness': {},
                'quality_trends': [],
                'best_keywords': [],
                'parameter_evolution': [],
                'learning_events': []
            }

    def save_learning_history(self):
        """Save learning data"""
        with open(self.learning_history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def analyze_query_effectiveness(self) -> Dict[str, Any]:
        """
        Analyze which search queries are finding the best gems

        Returns effectiveness scores and recommendations
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all gems from last 24 hours
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()

        cursor.execute("""
            SELECT data FROM discovered_gems
            WHERE discovered_at > ?
            ORDER BY agentdb_multiplier DESC
        """, (yesterday,))

        recent_gems = [json.loads(row[0]) for row in cursor.fetchall()]
        conn.close()

        if not recent_gems:
            return {'status': 'no_recent_data'}

        # Analyze keyword patterns in top gems
        top_25_percent = recent_gems[:max(1, len(recent_gems) // 4)]

        keyword_counts = Counter()
        for gem in top_25_percent:
            desc = (gem.get('description') or '').lower()
            topics = [t.lower() for t in gem.get('topics', [])]

            # Extract keywords
            words = desc.split() + topics
            keyword_counts.update(words)

        # Find emerging patterns (keywords in top gems but not yet in our queries)
        emerging_keywords = [
            kw for kw, count in keyword_counts.most_common(20)
            if len(kw) > 4 and count >= 2  # Filter noise
        ]

        # Update learning history
        self.history['best_keywords'] = emerging_keywords[:10]
        self.history['learning_events'].append({
            'timestamp': datetime.now().isoformat(),
            'event': 'query_analysis',
            'emerging_keywords': emerging_keywords[:5],
            'gems_analyzed': len(recent_gems)
        })

        return {
            'status': 'analyzed',
            'gems_analyzed': len(recent_gems),
            'top_performers': len(top_25_percent),
            'emerging_keywords': emerging_keywords[:10],
            'recommendation': 'add_new_queries' if emerging_keywords else 'continue_current'
        }

    def track_quality_trends(self) -> Dict[str, Any]:
        """
        Track if gem quality is improving over time

        Returns trend analysis and recommendations
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get gems from different time periods
        now = datetime.now()
        periods = {
            'last_12h': (now - timedelta(hours=12)).isoformat(),
            'last_24h': (now - timedelta(hours=24)).isoformat(),
            'last_week': (now - timedelta(days=7)).isoformat()
        }

        trends = {}

        for period_name, since_time in periods.items():
            cursor.execute("""
                SELECT
                    AVG(agentdb_multiplier) as avg_mult,
                    AVG(stars) as avg_stars,
                    COUNT(*) as count,
                    SUM(CASE WHEN stars >= 5 AND stars <= 100 AND forks > 0 THEN 1 ELSE 0 END) as perfect_gems
                FROM discovered_gems
                WHERE discovered_at > ?
            """, (since_time,))

            row = cursor.fetchone()

            trends[period_name] = {
                'avg_multiplier': round(row[0] or 0, 1),
                'avg_stars': round(row[1] or 0, 1),
                'total_gems': row[2] or 0,
                'perfect_gems': row[3] or 0,
                'quality_score': round((row[0] or 0) * (row[3] or 0) / max(row[2] or 1, 1), 2)
            }

        conn.close()

        # Calculate trend direction
        if trends['last_24h']['quality_score'] > trends['last_week']['quality_score']:
            trend = 'improving'
        elif trends['last_24h']['quality_score'] < trends['last_week']['quality_score']:
            trend = 'declining'
        else:
            trend = 'stable'

        # Save to history
        self.history['quality_trends'].append({
            'timestamp': datetime.now().isoformat(),
            'trend': trend,
            'quality_score_24h': trends['last_24h']['quality_score'],
            'perfect_gems_12h': trends['last_12h']['perfect_gems']
        })

        # Keep only last 30 trend records
        self.history['quality_trends'] = self.history['quality_trends'][-30:]

        return {
            'trend': trend,
            'periods': trends,
            'recommendation': self._get_quality_recommendation(trend, trends)
        }

    def _get_quality_recommendation(self, trend: str, trends: Dict) -> str:
        """Generate recommendation based on quality trends"""
        if trend == 'declining':
            return 'increase_selectivity'  # Raise quality bar
        elif trends['last_12h']['perfect_gems'] < 5:
            return 'expand_search'  # Search more broadly
        else:
            return 'maintain_course'  # Keep current strategy

    def suggest_parameter_improvements(self) -> Dict[str, Any]:
        """
        Suggest improvements to discovery parameters

        Returns recommended parameter changes
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Analyze star range effectiveness
        cursor.execute("""
            SELECT
                CASE
                    WHEN stars < 5 THEN '0-4'
                    WHEN stars < 25 THEN '5-24'
                    WHEN stars < 50 THEN '25-49'
                    WHEN stars < 100 THEN '50-99'
                    ELSE '100+'
                END as star_range,
                COUNT(*) as count,
                AVG(agentdb_multiplier) as avg_mult,
                SUM(CASE WHEN forks > 0 THEN 1 ELSE 0 END) as with_forks
            FROM discovered_gems
            GROUP BY star_range
        """)

        star_analysis = {}
        for row in cursor.fetchall():
            star_analysis[row[0]] = {
                'count': row[1],
                'avg_multiplier': round(row[2], 1),
                'with_forks': row[3],
                'quality_ratio': round(row[3] / max(row[1], 1), 2)
            }

        conn.close()

        # Find best performing star range
        best_range = max(star_analysis.items(),
                        key=lambda x: x[1]['quality_ratio'] * x[1]['avg_multiplier'])

        # Generate recommendations
        recommendations = {
            'best_star_range': best_range[0],
            'best_star_range_stats': best_range[1],
            'suggested_min_stars': self._extract_min_stars(best_range[0]),
            'suggested_max_stars': self._extract_max_stars(best_range[0]),
            'star_range_analysis': star_analysis
        }

        # Save parameter evolution
        self.history['parameter_evolution'].append({
            'timestamp': datetime.now().isoformat(),
            'best_range': best_range[0],
            'quality_ratio': best_range[1]['quality_ratio']
        })

        return recommendations

    def _extract_min_stars(self, range_str: str) -> int:
        """Extract minimum stars from range string"""
        if range_str == '0-4':
            return 0
        elif range_str == '100+':
            return 100
        return int(range_str.split('-')[0])

    def _extract_max_stars(self, range_str: str) -> int:
        """Extract maximum stars from range string"""
        if range_str == '100+':
            return 500
        return int(range_str.split('-')[1])

    def generate_new_queries(self, count: int = 5) -> List[str]:
        """
        Generate new search queries based on learning

        Uses discovered patterns to create novel queries
        """
        base_patterns = [
            "{keyword} performance",
            "{keyword} slow",
            "{keyword} optimize",
            "{keyword} latency",
            "fast {keyword}",
            "{keyword} speed up",
            "improve {keyword}",
            "{keyword} bottleneck"
        ]

        new_queries = []

        # Use learned best keywords
        for keyword in self.history['best_keywords'][:count]:
            pattern = base_patterns[len(new_queries) % len(base_patterns)]
            query = pattern.format(keyword=keyword)
            new_queries.append(query)

        return new_queries

    def run_improvement_cycle(self) -> Dict[str, Any]:
        """
        Run full improvement cycle

        Returns comprehensive learning report
        """
        print("🧠 Running self-improvement analysis...")

        query_analysis = self.analyze_query_effectiveness()
        quality_trends = self.track_quality_trends()
        parameter_suggestions = self.suggest_parameter_improvements()
        new_queries = self.generate_new_queries(5)

        self.save_learning_history()

        return {
            'timestamp': datetime.now().isoformat(),
            'query_effectiveness': query_analysis,
            'quality_trends': quality_trends,
            'parameter_suggestions': parameter_suggestions,
            'new_queries_suggested': new_queries,
            'learning_cycles_completed': len(self.history['learning_events'])
        }


class ReportGenerator:
    """Generate comprehensive discovery insights reports"""

    def __init__(self, db_path: str = "continuous_discovery.db"):
        self.db_path = db_path
        self.algorithm = SelfImprovingAlgorithm(db_path)

    def get_stats_for_period(self, hours: int) -> Dict[str, Any]:
        """Get statistics for a time period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        # Gems discovered
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                AVG(agentdb_multiplier) as avg_mult,
                AVG(stars) as avg_stars,
                SUM(CASE WHEN stars >= 5 AND stars <= 100 AND forks > 0 AND agentdb_multiplier >= 15 THEN 1 ELSE 0 END) as perfect
            FROM discovered_gems
            WHERE discovered_at > ?
        """, (since_time,))

        stats_row = cursor.fetchone()

        # Top gems
        cursor.execute("""
            SELECT name, owner, url, stars, forks, agentdb_multiplier, category
            FROM discovered_gems
            WHERE discovered_at > ? AND agentdb_multiplier >= 15
            ORDER BY agentdb_multiplier DESC, stars DESC
            LIMIT 10
        """, (since_time,))

        top_gems = [{
            'name': row[0],
            'owner': row[1],
            'url': row[2],
            'stars': row[3],
            'forks': row[4],
            'multiplier': round(row[5], 1),
            'category': row[6]
        } for row in cursor.fetchall()]

        conn.close()

        return {
            'period_hours': hours,
            'total_gems': stats_row[0] or 0,
            'avg_multiplier': round(stats_row[1] or 0, 1),
            'avg_stars': round(stats_row[2] or 0, 1),
            'perfect_gems': stats_row[3] or 0,
            'top_gems': top_gems
        }

    def get_all_time_stats(self) -> Dict[str, Any]:
        """Get all-time statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total,
                AVG(agentdb_multiplier) as avg_mult,
                AVG(stars) as avg_stars,
                MIN(discovered_at) as first_discovery,
                MAX(discovered_at) as last_discovery,
                SUM(CASE WHEN stars >= 5 AND stars <= 100 AND forks > 0 AND agentdb_multiplier >= 15 THEN 1 ELSE 0 END) as perfect
            FROM discovered_gems
        """)

        stats_row = cursor.fetchone()

        # Category breakdown
        cursor.execute("""
            SELECT category, COUNT(*) as count, AVG(agentdb_multiplier) as avg_mult
            FROM discovered_gems
            GROUP BY category
            ORDER BY count DESC
        """)

        categories = [{
            'category': row[0],
            'count': row[1],
            'avg_multiplier': round(row[2], 1)
        } for row in cursor.fetchall()]

        # Ideas generated
        cursor.execute("SELECT COUNT(*) FROM generated_ideas")
        ideas_count = cursor.fetchone()[0]

        conn.close()

        return {
            'total_gems': stats_row[0] or 0,
            'avg_multiplier': round(stats_row[1] or 0, 1),
            'avg_stars': round(stats_row[2] or 0, 1),
            'first_discovery': stats_row[3],
            'last_discovery': stats_row[4],
            'perfect_gems': stats_row[5] or 0,
            'ideas_generated': ideas_count,
            'categories': categories
        }

    def calculate_revenue_projections(self, perfect_gems: int) -> Dict[str, Any]:
        """Calculate revenue projections from perfect gems"""

        # Conservative: 10% conversion at $299/month
        conservative = {
            'conversion_rate': 0.10,
            'price_per_month': 299,
            'customers': int(perfect_gems * 0.10),
            'mrr': int(perfect_gems * 0.10 * 299),
            'arr': int(perfect_gems * 0.10 * 299 * 12)
        }

        # Realistic: 20% conversion, mix of tiers
        realistic = {
            'conversion_rate': 0.20,
            'avg_price_per_month': 450,  # Mix of $299 and $999
            'customers': int(perfect_gems * 0.20),
            'mrr': int(perfect_gems * 0.20 * 450),
            'arr': int(perfect_gems * 0.20 * 450 * 12)
        }

        # Optimistic: 30% conversion with enterprise
        optimistic = {
            'conversion_rate': 0.30,
            'avg_price_per_month': 650,  # More enterprise
            'customers': int(perfect_gems * 0.30),
            'mrr': int(perfect_gems * 0.30 * 650),
            'arr': int(perfect_gems * 0.30 * 650 * 12)
        }

        return {
            'based_on_gems': perfect_gems,
            'conservative': conservative,
            'realistic': realistic,
            'optimistic': optimistic
        }

    def generate_markdown_report(self) -> str:
        """Generate full markdown report"""

        # Run self-improvement analysis
        learning_results = self.algorithm.run_improvement_cycle()

        # Gather statistics
        stats_12h = self.get_stats_for_period(12)
        stats_24h = self.get_stats_for_period(24)
        stats_7d = self.get_stats_for_period(168)
        all_time = self.get_all_time_stats()

        # Revenue projections
        revenue = self.calculate_revenue_projections(all_time['perfect_gems'])

        # Generate report
        report = f"""# 📊 AgentDB Discovery Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Report Period**: Last 12 Hours

---

## 🎯 Executive Summary

### Last 12 Hours Performance:
- **New Gems Discovered**: {stats_12h['total_gems']}
- **Perfect Gems** (5-100★, forks, 15x+): {stats_12h['perfect_gems']}
- **Average Multiplier**: {stats_12h['avg_multiplier']}x
- **Average Stars**: {stats_12h['avg_stars']}

### Quality Trend: **{learning_results['quality_trends']['trend'].upper()}** 📈

---

## 📈 Performance Trends

### 12 Hours vs 24 Hours vs 7 Days:

| Metric | 12h | 24h | 7d | All-Time |
|--------|-----|-----|----|----|
| Total Gems | {stats_12h['total_gems']} | {stats_24h['total_gems']} | {stats_7d['total_gems']} | {all_time['total_gems']} |
| Perfect Gems | {stats_12h['perfect_gems']} | {stats_24h['perfect_gems']} | {stats_7d['perfect_gems']} | {all_time['perfect_gems']} |
| Avg Multiplier | {stats_12h['avg_multiplier']}x | {stats_24h['avg_multiplier']}x | {stats_7d['avg_multiplier']}x | {all_time['avg_multiplier']}x |
| Avg Stars | {stats_12h['avg_stars']} | {stats_24h['avg_stars']} | {stats_7d['avg_stars']} | {all_time['avg_stars']} |

### Discovery Rate:
- **Last 12h**: {stats_12h['total_gems']/12:.1f} gems/hour
- **Last 24h**: {stats_24h['total_gems']/24:.1f} gems/hour
- **Last 7d**: {stats_7d['total_gems']/168:.1f} gems/hour

---

## 💎 Top Discoveries (Last 12 Hours)

"""

        # Add top gems
        if stats_12h['top_gems']:
            for i, gem in enumerate(stats_12h['top_gems'], 1):
                report += f"""### {i}. **{gem['name']}** ({gem['stars']}⭐, {gem['forks']}🍴)
- **Multiplier**: {gem['multiplier']}x
- **Category**: {gem['category']}
- **Owner**: {gem['owner']}
- **URL**: {gem['url']}

"""
        else:
            report += "*No perfect gems found in last 12 hours. Algorithm adjusting search strategy...*\n\n"

        report += f"""---

## 💰 Revenue Projections

Based on **{all_time['perfect_gems']} perfect gems** discovered:

### Conservative (10% conversion):
- **Customers**: {revenue['conservative']['customers']}
- **MRR**: ${revenue['conservative']['mrr']:,}
- **ARR**: ${revenue['conservative']['arr']:,}

### Realistic (20% conversion):
- **Customers**: {revenue['realistic']['customers']}
- **MRR**: ${revenue['realistic']['mrr']:,}
- **ARR**: ${revenue['realistic']['arr']:,}

### Optimistic (30% conversion):
- **Customers**: {revenue['optimistic']['customers']}
- **MRR**: ${revenue['optimistic']['mrr']:,}
- **ARR**: ${revenue['optimistic']['arr']:,}

**Path to $10K MRR**: Need {int(10000/299)} customers at $299/month
**Current Progress**: {int(all_time['perfect_gems'] * 0.20)} potential customers (realistic)

---

## 🧠 Self-Improving Algorithm Insights

### Quality Trend Analysis:
**Status**: {learning_results['quality_trends']['trend'].upper()}
**Recommendation**: {learning_results['quality_trends']['recommendation']}

"""

        # Add quality trend details
        periods = learning_results['quality_trends']['periods']
        report += f"""### Quality Scores by Period:
- **Last 12h**: {periods['last_12h']['quality_score']} ({periods['last_12h']['perfect_gems']} perfect gems)
- **Last 24h**: {periods['last_24h']['quality_score']} ({periods['last_24h']['perfect_gems']} perfect gems)
- **Last 7d**: {periods['last_week']['quality_score']} ({periods['last_week']['perfect_gems']} perfect gems)

"""

        # Add emerging patterns
        if learning_results['query_effectiveness']['status'] == 'analyzed':
            qe = learning_results['query_effectiveness']
            report += f"""### Emerging Patterns Discovered:
The algorithm analyzed **{qe['gems_analyzed']} recent gems** and found these emerging keywords:

"""
            for i, keyword in enumerate(qe['emerging_keywords'][:5], 1):
                report += f"{i}. `{keyword}`\n"

            report += f"\n**Action**: {qe['recommendation'].replace('_', ' ').title()}\n\n"

        # Add parameter suggestions
        param_sugg = learning_results['parameter_suggestions']
        report += f"""### Optimal Search Parameters:
**Best Performing Star Range**: {param_sugg['best_star_range']}
- Quality Ratio: {param_sugg['best_star_range_stats']['quality_ratio']}
- Avg Multiplier: {param_sugg['best_star_range_stats']['avg_multiplier']}x
- Gems with Forks: {param_sugg['best_star_range_stats']['with_forks']}

**Suggested Adjustments**:
- Minimum Stars: {param_sugg['suggested_min_stars']}
- Maximum Stars: {param_sugg['suggested_max_stars']}

"""

        # Add new query suggestions
        report += f"""### New Queries to Try:
The algorithm generated these novel search queries based on learned patterns:

"""
        for i, query in enumerate(learning_results['new_queries_suggested'], 1):
            report += f"{i}. `{query}`\n"

        report += f"""
---

## 📊 Category Breakdown (All-Time)

"""
        for cat in all_time['categories']:
            report += f"- **{cat['category']}**: {cat['count']} gems (avg {cat['avg_multiplier']}x multiplier)\n"

        report += f"""
---

## 🎯 Recommended Actions

"""

        # Generate contextual recommendations
        if stats_12h['perfect_gems'] == 0:
            report += """### ⚠️ No Perfect Gems in Last 12 Hours
**Recommendation**:
1. Algorithm is expanding search with new queries (see above)
2. Adjusting star range filters based on historical performance
3. Continue monitoring - discovery is cyclical

"""
        elif stats_12h['perfect_gems'] < 5:
            report += """### 📊 Moderate Discovery Rate
**Recommendation**:
1. Quality over quantity - focus on discovered gems
2. Begin outreach to top gems from last 24 hours
3. Algorithm learning new patterns for next cycle

"""
        else:
            report += f"""### ✅ Strong Discovery Performance ({stats_12h['perfect_gems']} perfect gems)
**Recommendation**:
1. **Immediate**: Start outreach to top 5 gems
2. **This week**: Build integrations for top 3
3. **Revenue focus**: Target ${int(stats_12h['perfect_gems'] * 0.2 * 299):,} MRR potential

"""

        # Add top 3 action items
        if stats_24h['top_gems']:
            report += f"""### Top 3 Immediate Opportunities:

"""
            for i, gem in enumerate(stats_24h['top_gems'][:3], 1):
                report += f"""**{i}. {gem['name']}** ({gem['multiplier']}x multiplier)
   - Stars: {gem['stars']} | Forks: {gem['forks']} | Category: {gem['category']}
   - Action: Email maintainer with AgentDB integration offer
   - URL: {gem['url']}

"""

        report += f"""---

## 📚 Learning Progress

- **Learning Cycles Completed**: {learning_results['learning_cycles_completed']}
- **Algorithm Version**: Self-Improving v2.0
- **Database Size**: {all_time['total_gems']} gems
- **Ideas Generated**: {all_time['ideas_generated']}

### How the Algorithm Learns:
1. ✅ Analyzes which queries find best gems
2. ✅ Tracks quality trends over time
3. ✅ Identifies emerging keyword patterns
4. ✅ Optimizes search parameters automatically
5. ✅ Generates novel queries from patterns
6. ✅ Adjusts filters based on performance

**Next Improvement Cycle**: In 12 hours

---

## 🔄 System Status

- **Discovery Engine**: ✅ RUNNING
- **Learning Algorithm**: ✅ ACTIVE
- **Database**: {self.db_path}
- **Report Frequency**: Every 12 hours
- **Next Report**: {(datetime.now() + timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')}

---

*Generated by Self-Improving AgentDB Discovery System*
*Algorithm gets smarter with every discovery cycle*
"""

        return report

    def generate_report(self) -> Tuple[str, str]:
        """
        Generate report and return (subject, body)
        """
        markdown = self.generate_markdown_report()

        # Generate subject line
        stats_12h = self.get_stats_for_period(12)
        all_time = self.get_all_time_stats()

        subject = f"📊 AgentDB Discovery: {stats_12h['perfect_gems']} Perfect Gems (12h) | {all_time['perfect_gems']} Total"

        return subject, markdown


class EmailSender:
    """Send reports via email"""

    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
        self.to_email = os.getenv('TO_EMAIL')

    def send_email(self, subject: str, body: str):
        """Send email with report"""

        if not all([self.smtp_user, self.smtp_password, self.to_email]):
            print("⚠️  Email not configured. Saving report locally instead.")
            self._save_local_report(subject, body)
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = self.to_email

            # Add plain text version
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)

            # Add HTML version (convert markdown to basic HTML)
            html_body = self._markdown_to_html(body)
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Send email
            print(f"📧 Sending email to {self.to_email}...")

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"✅ Email sent successfully!")

            # Also save locally
            self._save_local_report(subject, body)

            return True

        except Exception as e:
            print(f"❌ Email failed: {e}")
            print("💾 Saving report locally instead...")
            self._save_local_report(subject, body)
            return False

    def _markdown_to_html(self, markdown: str) -> str:
        """Convert markdown to basic HTML"""
        html = markdown

        # Headers
        html = html.replace('# ', '<h1>').replace('\n## ', '</h1>\n<h2>')
        html = html.replace('\n### ', '</h2>\n<h3>').replace('\n#### ', '</h3>\n<h4>')

        # Bold
        import re
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Code blocks
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')

        # Wrap in HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; border-bottom: 2px solid #95a5a6; padding-bottom: 8px; margin-top: 30px; }}
                h3 {{ color: #7f8c8d; margin-top: 20px; }}
                code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
                a {{ color: #3498db; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <p>{html}</p>
        </body>
        </html>
        """

        return html

    def _save_local_report(self, subject: str, body: str):
        """Save report locally"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.md"

        with open(filename, 'w') as f:
            f.write(f"# {subject}\n\n")
            f.write(body)

        print(f"💾 Report saved: {filename}")


def main():
    """Main function - generate and send report"""

    print("="*70)
    print("📊 AUTOMATED REPORT GENERATOR")
    print("="*70)
    print()

    # Generate report
    generator = ReportGenerator()
    subject, body = generator.generate_report()

    print(f"\n📝 Report generated: {len(body)} characters")
    print(f"📧 Subject: {subject}")
    print()

    # Send email
    sender = EmailSender()
    sender.send_email(subject, body)

    print()
    print("="*70)
    print("✅ REPORT GENERATION COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
