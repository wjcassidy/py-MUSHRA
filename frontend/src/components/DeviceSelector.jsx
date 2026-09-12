export default function DeviceSelector({ devices, selectedIndex, onChange }) {
  return (
    <div className="device-selector">
      <label htmlFor="device-select">Output device</label>
      <select
        id="device-select"
        value={selectedIndex ?? ''}
        onChange={(e) => onChange(e.target.value === '' ? null : Number(e.target.value))}
      >
        <option value="">System default</option>
        {devices.map((d) => (
          <option key={d.index} value={d.index}>
            {d.name} ({d.max_output_channels} ch)
          </option>
        ))}
      </select>
    </div>
  )
}
