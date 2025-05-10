# LiveTicket

LiveTicket is a Python-based simulator designed to calculate and visualize the probability of winning tickets in a multi-stage live event lottery. It allows users to configure various parameters related to the event, fan base, and lottery stages to estimate their chances of success.

## Features

- **Multi-Stage Lottery Simulation:** Simulates complex lotteries with multiple selection rounds.
- **Configurable Parameters:**
  - Overall event attendance and number of shows.
  - Core fan population.
  - User's targeted events (e.g., specific cities/dates).
  - Detailed lottery stage definitions:
    - Name of the stage.
    - Percentage of core fans applying.
    - Number of additional (non-core) applicants.
    - Weight/priority for seat allocation in that stage.
- **Duplicate Win Consideration:** Option to simulate scenarios where winning in one stage might affect eligibility or seat availability in subsequent stages (e.g., by reducing the effective seat pool for new winners).
- **Scenario Comparison:** Run and compare results from multiple simulation configurations (e.g., with and without duplicate win considerations).
- **Text-Based Results:** Clear console output detailing probabilities for winning at each stage and the overall probability of not winning at all.
- **Graphical Visualization:** Generates a bar chart comparing the win probabilities across different stages for various scenarios.
- **JSON Configuration:** Easily configure all simulation parameters through a `config.json` file.

## Prerequisites

- Python 3.x
- The following Python packages:
  - `matplotlib` (for plotting graphs)
  - `numpy` (for numerical operations)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Blacook/LiveTicket.git
    cd LiveTicket
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    Then install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The simulation is configured using a `config.json` file in the root directory of the project. If this file is not found, the simulator will use default values (as defined in `src/__main__.py`).

Here's an example structure for `config.json`:

```json
{
  "simulation_settings": {
    "total_overall_attendance": 550000,
    "num_total_events": 12,
    "core_fan_total_population": 1000000
  },
  "user_target_events_details": {
    "tokyo": 4,
    "nagoya": 2,
    "osaka": 2
  },
  "lottery_stages_definition": [
    {
      "name": "1次(CD+年会員)",
      "applicant_core_fan_ratio": 0.3,
      "additional_applicants": 0,
      "weight": 5
    },
    {
      "name": "2次(CD+全会員)",
      "applicant_core_fan_ratio": 0.5,
      "additional_applicants": 0,
      "weight": 4
    },
    {
      "name": "3次(全会員)",
      "applicant_core_fan_ratio": 0.9,
      "additional_applicants": 0,
      "weight": 3
    },
    {
      "name": "4次(全+Ponta)",
      "applicant_core_fan_ratio": 1.0,
      "additional_applicants": 500000,
      "weight": 2
    },
    {
      "name": "5次(任意)",
      "applicant_core_fan_ratio": 1.0,
      "additional_applicants": 1000000,
      "weight": 1
    }
  ],
  "simulation_cases_to_run": [
    {
      "case_name": "重複当選なし",
      "duplicate_config": {}
    },
    {
      "case_name": "重複当選あり (新規枠10%減)",
      "duplicate_config": {
        "type": "seat_reduction",
        "rate": 0.1
      }
    }
  ]
}
```

**Key Configuration Fields:**

- `simulation_settings`: Basic parameters for the overall event and fan base.
- `user_target_events_details`: How many events the user is applying for in different regions/categories.
- `lottery_stages_definition`: An array defining each lottery stage with its specific parameters.
  - `name`: Display name for the stage.
  - `applicant_core_fan_ratio`: Proportion (0.0 to 1.0) of core fans expected to apply in this stage.
  - `additional_applicants`: Number of non-core fans applying in this stage.
  - `weight`: A numerical weight determining the proportion of total available seats allocated to this stage.
- `simulation_cases_to_run`: An array defining different scenarios to simulate and compare.
  - `case_name`: A descriptive name for the scenario.
  - `duplicate_config`: Configuration for handling duplicate wins.
    - `type: "seat_reduction"`: Reduces the number of seats available for new winners in each stage.
    - `rate`: The percentage (0.0 to 1.0) by which seats are reduced if `type` is `seat_reduction`.

## Usage

To run the simulator, navigate to the project's root directory and execute the `src` package as a module:

```bash
python3 -m src
```

The simulator will read `config.json` (or use defaults), run the defined simulation cases, print the results to the console, and display a comparison graph if multiple cases are run.

## Testing

To run the unit tests, navigate to the project's root directory and use the `unittest` module:

```bash
python3 -m unittest discover tests
```

This will automatically find and run all tests located in the `tests` directory.

## Troubleshooting

- **Graph Font Issues:** If Japanese characters (or other non-ASCII characters) do not display correctly in the output graph, you may need to ensure appropriate fonts are installed on your system and configured for Matplotlib. The simulator attempts to use common Japanese fonts, but you might need to adjust the font settings in `src/utils/plotter.py` if issues persist.
