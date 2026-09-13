export default function DeviceSelector({ devices, selectedIndex, onChange, channelStatus }) {
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
      {channelStatus && (
        <div
          className={`device-selector__status${
            channelStatus.error || channelStatus.monitor_channels
              ? ' device-selector__status--invalid'
              : ' device-selector__status--valid'
          }`}
        >
          {channelStatus.error
            ? '(invalid)'
            : channelStatus.monitor_channels
            ? '(invalid; using stereo output)'
            : '(valid)'}
          <div className="device-selector__panel">
            <div>Detected inputs: {channelStatus.detected_input_channels ?? '?'}</div>
            <div>Device outputs: {channelStatus.device_output_channels ?? '?'}</div>
            <div>Required outputs: {channelStatus.required_output_channels ?? '?'}</div>
            <div>Plugin preset: {channelStatus.plugin_preset ?? 'none'}</div>
            {!channelStatus.error && channelStatus.monitor_channels && (
              <div>
                Using first {channelStatus.monitor_channels} of {channelStatus.required_output_channels}{' '}
                channels (validation only)
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
