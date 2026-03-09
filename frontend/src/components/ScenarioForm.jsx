const CATEGORY_OPTIONS = [
  "deli_salad",
  "dairy_dip",
  "acidified_sauce",
  "rte_meat",
  "plant_based_spread",
  "smoked_seafood",
  "cooked_poultry",
  "mayo_dressing",
  "hummus_dip",
  "soft_cheese",
];

const PACKAGING_OPTIONS = ["tub", "vacuum", "jar", "MAP", "tray", "bottle", "foil", "sachet"];
const OXYGEN_OPTIONS = ["aerobic", "anaerobic", "reduced_oxygen"];
const INOCULATION_OPTIONS = ["low_inoculum", "medium_inoculum", "high_inoculum"];
const PRESERVATIVE_OPTIONS = ["none", "sodium_benzoate", "nisin", "potassium_sorbate", "cultured_dextrose"];
const ACIDULANT_OPTIONS = ["none", "vinegar", "lactic_acid", "acetic_acid", "citric_acid"];
const CURVE_MODE_OPTIONS = ["both", "ml", "kinetic"];

export function ScenarioForm({ formData, onChange, onSubmit, loading }) {
  return (
    <form className="scenario-form" onSubmit={onSubmit}>
      <div className="form-grid">
        <label>
          Product Category
          <select name="product_category" value={formData.product_category} onChange={onChange}>
            {CATEGORY_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          pH
          <input name="ph" type="number" step="0.01" value={formData.ph} onChange={onChange} />
        </label>
        <label>
          aw
          <input name="aw" type="number" step="0.001" value={formData.aw} onChange={onChange} />
        </label>
        <label>
          Salt %
          <input name="salt_percent" type="number" step="0.01" value={formData.salt_percent} onChange={onChange} />
        </label>
        <label>
          Sugar %
          <input name="sugar_percent" type="number" step="0.01" value={formData.sugar_percent} onChange={onChange} />
        </label>
        <label>
          Fat %
          <input name="fat_percent" type="number" step="0.01" value={formData.fat_percent} onChange={onChange} />
        </label>
        <label>
          Preservative Enabled
          <select name="preservative_flag" value={String(formData.preservative_flag)} onChange={onChange}>
            <option value="false">false</option>
            <option value="true">true</option>
          </select>
        </label>
        <label>
          Preservative Type
          <select name="preservative_type" value={formData.preservative_type} onChange={onChange}>
            {PRESERVATIVE_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          Acidulant
          <select name="acidulant_type" value={formData.acidulant_type} onChange={onChange}>
            {ACIDULANT_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          Packaging
          <select name="packaging_type" value={formData.packaging_type} onChange={onChange}>
            {PACKAGING_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          Oxygen Condition
          <select name="oxygen_condition" value={formData.oxygen_condition} onChange={onChange}>
            {OXYGEN_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          Storage Temperature C
          <input
            name="storage_temperature_c"
            type="number"
            step="0.1"
            value={formData.storage_temperature_c}
            onChange={onChange}
          />
        </label>
        <label>
          Inoculation Type
          <select name="inoculation_type" value={formData.inoculation_type} onChange={onChange}>
            {INOCULATION_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          Initial Inoculum (log CFU/g)
          <input
            name="initial_inoculum_log_cfu_g"
            type="number"
            step="0.01"
            value={formData.initial_inoculum_log_cfu_g}
            onChange={onChange}
          />
        </label>
        <label>
          Target Shelf Life Days
          <input name="target_shelf_life_days" type="number" value={formData.target_shelf_life_days} onChange={onChange} />
        </label>
        <label>
          Curve Mode
          <select name="curve_mode" value={formData.curve_mode} onChange={onChange}>
            {CURVE_MODE_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
      </div>
      <button className="primary-button" type="submit" disabled={loading}>
        {loading ? "Running simulation..." : "Run shelf-life simulation"}
      </button>
    </form>
  );
}
