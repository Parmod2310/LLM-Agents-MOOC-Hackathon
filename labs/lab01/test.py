import pytest
from main import fetch_restaurant_data, calculate_overall_score


@pytest.mark.parametrize("restaurant_name, expected_in_result", [
    ("Taco Bell", True),            # Existing restaurant
    ("NonExistentRestaurant", False),  # Non-existing restaurant
    ("taco bell", True),            # Case-insensitive match
    ("Bell", False)                 # Partial name should not match
])
def test_fetch_restaurant_data(restaurant_name, expected_in_result):

    result = fetch_restaurant_data(restaurant_name)
    if expected_in_result:
        assert restaurant_name.title() in result, f"Expected {restaurant_name.title()} to be in the result"
        assert len(result[restaurant_name.title()]) > 0, f"Expected reviews for {restaurant_name.title()}"
    else:
        assert result == {}, f"Expected an empty dictionary for {restaurant_name}"


@pytest.mark.parametrize("restaurant_name, food_scores, service_scores, expected_score_range", [
    ("Taco Bell", [4, 5, 3], [3, 4, 4], (1.0, 5.0)),  # Valid scores
    ("Boundary Restaurant", [1, 5], [1, 5], (1.0, 5.0))  # Boundary values
])
def test_calculate_overall_score_valid_inputs(restaurant_name, food_scores, service_scores, expected_score_range):

    result = calculate_overall_score(restaurant_name, food_scores, service_scores)
    assert restaurant_name in result, f"Expected {restaurant_name} to be in the result"
    score = float(result[restaurant_name])
    assert expected_score_range[0] <= score <= expected_score_range[1], f"Score should be between {expected_score_range[0]} and {expected_score_range[1]}"

def test_calculate_overall_score_empty_scores():

    with pytest.raises(ValueError, match="Food scores and customer service scores must have the same non-zero length"):
        calculate_overall_score("Taco Bell", [], [])

def test_calculate_overall_score_mismatched_lengths():
    food_scores = [4, 5]
    service_scores = [3]
    with pytest.raises(ValueError, match="Food scores and customer service scores must have the same non-zero length"):
        calculate_overall_score("Taco Bell", food_scores, service_scores)

# Run the tests
if __name__ == "__main__":
    pytest.main()
