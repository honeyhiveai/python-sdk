"""
Performance test demonstrating the improvement from batch fetching
vs individual API calls for large datasets.
"""
import time
from unittest.mock import Mock, patch

def test_individual_vs_batch_performance():
    """Compare performance of individual vs batch fetching for large datasets"""
    
    num_datapoints = 100
    
    print(f"Performance comparison for {num_datapoints} datapoints:")
    print("=" * 60)
    
    # Simulate individual API calls (old approach)
    start_time = time.time()
    individual_call_time = 0.01  # 10ms per API call
    for i in range(num_datapoints):
        time.sleep(individual_call_time)  # Simulate API call
    individual_total_time = time.time() - start_time
    
    print(f"Individual API calls: {individual_total_time:.2f} seconds")
    print(f"  - {num_datapoints} calls × {individual_call_time*1000:.0f}ms = {individual_total_time:.2f}s")
    
    # Simulate batch API call (new approach)
    start_time = time.time()
    batch_call_time = 0.05  # 50ms for one batch call
    time.sleep(batch_call_time)  # Simulate single batch API call
    batch_total_time = time.time() - start_time
    
    print(f"Batch API call: {batch_total_time:.2f} seconds")
    print(f"  - 1 call × {batch_call_time*1000:.0f}ms = {batch_total_time:.2f}s")
    
    # Calculate improvement
    improvement_factor = individual_total_time / batch_total_time
    time_saved = individual_total_time - batch_total_time
    
    print(f"\nImprovement:")
    print(f"  - {improvement_factor:.1f}x faster")
    print(f"  - {time_saved:.2f} seconds saved")
    print(f"  - {(time_saved/individual_total_time)*100:.1f}% faster")
    
    # Show what happens with even larger datasets
    print(f"\nProjected performance for larger datasets:")
    for size in [500, 1000, 2000]:
        individual_time = size * individual_call_time
        batch_time = batch_call_time  # Same regardless of size
        improvement = individual_time / batch_time
        print(f"  - {size:4d} datapoints: {improvement:.1f}x faster ({individual_time:.1f}s → {batch_time:.2f}s)")

if __name__ == "__main__":
    test_individual_vs_batch_performance()