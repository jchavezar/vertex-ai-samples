class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = new Float32Array();
    this.port.onmessage = (e) => {
      const newData = e.data;
      const newBuffer = new Float32Array(this.buffer.length + newData.length);
      newBuffer.set(this.buffer);
      newBuffer.set(newData, this.buffer.length);
      this.buffer = newBuffer;
    };
  }

  process(inputs, outputs, parameters) {
    const output = outputs[0];
    const channel = output[0];

    if (this.buffer.length >= channel.length) {
      channel.set(this.buffer.subarray(0, channel.length));
      this.buffer = this.buffer.subarray(channel.length);
      return true;
    }

    if (this.buffer.length > 0) {
      channel.set(this.buffer);
      channel.fill(0, this.buffer.length);
      this.buffer = new Float32Array();
    }

    return true;
  }
}

registerProcessor('pcm-processor', PCMProcessor);
