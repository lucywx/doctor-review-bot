"""
Performance testing script
Tests response time, cache performance, and concurrent load
"""

import asyncio
import time
import statistics
from typing import List, Dict
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


class PerformanceTester:
    """Performance testing utility"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []

    async def test_health_check(self) -> bool:
        """Test if server is running"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    logger.info("✅ Server is healthy")
                    return True
                else:
                    logger.error(f"❌ Server unhealthy: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to server: {e}")
            return False

    async def send_whatsapp_message(
        self,
        doctor_name: str,
        from_number: str = "+1234567890"
    ) -> Dict:
        """Send a test WhatsApp message"""
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/webhook/whatsapp/test",
                    json={
                        "from": from_number,
                        "text": doctor_name
                    }
                )

                elapsed_ms = int((time.time() - start_time) * 1000)

                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time_ms": elapsed_ms,
                    "doctor_name": doctor_name
                }

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": elapsed_ms,
                "doctor_name": doctor_name
            }

    async def test_cache_performance(self):
        """Test cache hit vs cache miss performance"""
        logger.info("\n📊 Testing cache performance...")

        doctor_names = ["张医生", "李医生", "王医生"]

        # First query (cache miss)
        logger.info("\n1️⃣ First queries (cache miss):")
        miss_times = []
        for name in doctor_names:
            result = await self.send_whatsapp_message(name)
            miss_times.append(result["response_time_ms"])
            status = "✅" if result["success"] else "❌"
            logger.info(f"  {status} {name}: {result['response_time_ms']}ms")

        # Second query (cache hit)
        await asyncio.sleep(1)
        logger.info("\n2️⃣ Second queries (cache hit):")
        hit_times = []
        for name in doctor_names:
            result = await self.send_whatsapp_message(name)
            hit_times.append(result["response_time_ms"])
            status = "✅" if result["success"] else "❌"
            logger.info(f"  {status} {name}: {result['response_time_ms']}ms")

        # Analysis
        avg_miss = statistics.mean(miss_times)
        avg_hit = statistics.mean(hit_times)
        speedup = avg_miss / avg_hit if avg_hit > 0 else 0

        logger.info(f"\n📈 Cache Performance:")
        logger.info(f"  Average cache miss: {avg_miss:.0f}ms")
        logger.info(f"  Average cache hit:  {avg_hit:.0f}ms")
        logger.info(f"  Speedup: {speedup:.1f}x faster")

        return {
            "cache_miss_avg_ms": avg_miss,
            "cache_hit_avg_ms": avg_hit,
            "speedup": speedup
        }

    async def test_concurrent_load(self, num_users: int = 10):
        """Test concurrent user load"""
        logger.info(f"\n🔥 Testing concurrent load ({num_users} users)...")

        # Create tasks for concurrent requests
        tasks = []
        doctor_names = ["张医生", "李医生", "王医生", "赵医生", "刘医生"]

        for i in range(num_users):
            name = doctor_names[i % len(doctor_names)]
            from_number = f"+123456789{i:02d}"
            tasks.append(self.send_whatsapp_message(name, from_number))

        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Analysis
        success_count = sum(1 for r in results if r["success"])
        response_times = [r["response_time_ms"] for r in results if r["success"]]

        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            p95_time = sorted(response_times)[int(len(response_times) * 0.95)]

            logger.info(f"\n📊 Concurrent Load Results:")
            logger.info(f"  Total requests: {num_users}")
            logger.info(f"  Successful: {success_count}")
            logger.info(f"  Failed: {num_users - success_count}")
            logger.info(f"  Total time: {total_time:.2f}s")
            logger.info(f"  Avg response: {avg_time:.0f}ms")
            logger.info(f"  Min response: {min_time:.0f}ms")
            logger.info(f"  Max response: {max_time:.0f}ms")
            logger.info(f"  P95 response: {p95_time:.0f}ms")

            return {
                "total_requests": num_users,
                "successful": success_count,
                "failed": num_users - success_count,
                "total_time_s": total_time,
                "avg_response_ms": avg_time,
                "min_response_ms": min_time,
                "max_response_ms": max_time,
                "p95_response_ms": p95_time
            }
        else:
            logger.error("❌ All requests failed")
            return None

    async def test_response_consistency(self, num_runs: int = 5):
        """Test response consistency"""
        logger.info(f"\n🔄 Testing response consistency ({num_runs} runs)...")

        times = []
        for i in range(num_runs):
            result = await self.send_whatsapp_message("李医生")
            times.append(result["response_time_ms"])
            status = "✅" if result["success"] else "❌"
            logger.info(f"  Run {i+1}: {status} {result['response_time_ms']}ms")
            await asyncio.sleep(0.5)

        if times:
            avg = statistics.mean(times)
            stdev = statistics.stdev(times) if len(times) > 1 else 0
            cv = (stdev / avg * 100) if avg > 0 else 0

            logger.info(f"\n📊 Consistency:")
            logger.info(f"  Average: {avg:.0f}ms")
            logger.info(f"  Std Dev: {stdev:.0f}ms")
            logger.info(f"  CV: {cv:.1f}%")

            return {
                "avg_ms": avg,
                "stdev_ms": stdev,
                "coefficient_variation": cv
            }

    async def run_all_tests(self):
        """Run all performance tests"""
        logger.info("🚀 Starting performance tests...\n")

        # Check server health
        if not await self.test_health_check():
            logger.error("❌ Server not available. Please start the server first.")
            return

        results = {}

        try:
            # Test 1: Cache performance
            results["cache"] = await self.test_cache_performance()

            # Test 2: Concurrent load
            results["concurrent"] = await self.test_concurrent_load(num_users=10)

            # Test 3: Response consistency
            results["consistency"] = await self.test_response_consistency(num_runs=5)

            # Summary
            logger.info("\n" + "="*60)
            logger.info("📋 PERFORMANCE TEST SUMMARY")
            logger.info("="*60)

            if results.get("cache"):
                logger.info(f"\n✅ Cache Performance:")
                logger.info(f"   - Cache speedup: {results['cache']['speedup']:.1f}x")

            if results.get("concurrent"):
                logger.info(f"\n✅ Concurrent Load (10 users):")
                logger.info(f"   - Success rate: {results['concurrent']['successful']}/{results['concurrent']['total_requests']}")
                logger.info(f"   - Avg response: {results['concurrent']['avg_response_ms']:.0f}ms")
                logger.info(f"   - P95 response: {results['concurrent']['p95_response_ms']:.0f}ms")

            if results.get("consistency"):
                logger.info(f"\n✅ Response Consistency:")
                logger.info(f"   - Avg response: {results['consistency']['avg_ms']:.0f}ms")
                logger.info(f"   - Variation: {results['consistency']['coefficient_variation']:.1f}%")

            logger.info("\n" + "="*60)
            logger.info("🎉 All tests completed!")
            logger.info("="*60 + "\n")

        except Exception as e:
            logger.error(f"\n❌ Test error: {e}", exc_info=True)


async def main():
    """Main test runner"""
    tester = PerformanceTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
