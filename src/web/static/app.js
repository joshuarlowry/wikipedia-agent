// Wikipedia Research Agent - Web UI JavaScript

class WikipediaAgentUI {
    constructor() {
        this.elements = {
            queryInput: document.getElementById('query-input'),
            submitBtn: document.getElementById('submit-btn'),
            clearBtn: document.getElementById('clear-btn'),
            responseContainer: document.getElementById('response-container'),
            statusText: document.getElementById('status-text'),
            statusDot: document.querySelector('.status-dot'),
            providerInfo: document.getElementById('provider-info'),
            streamCheckbox: document.getElementById('stream-checkbox'),
            outputFormatRadios: document.getElementsByName('output-format'),
            providerSelect: document.getElementById('provider-select'),
            modelSelect: document.getElementById('model-select'),
        };

        this.isProcessing = false;
        this.currentProvider = null;
        this.currentModel = null;
        this.defaultModels = {
            openrouter: null,
            ollama: null,
        };
        this.init();
    }

    init() {
        // Set up event listeners
        this.elements.submitBtn.addEventListener('click', () => this.handleSubmit());
        this.elements.clearBtn.addEventListener('click', () => this.clearResponse());
        this.elements.queryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                this.handleSubmit();
            }
        });

        // Provider change handler
        if (this.elements.providerSelect) {
            this.elements.providerSelect.addEventListener('change', () => {
                this.handleProviderChange(this.elements.providerSelect.value);
            });
        }

        // Add click handlers for example questions
        document.querySelectorAll('.examples li').forEach(li => {
            li.addEventListener('click', () => {
                this.elements.queryInput.value = li.textContent;
                this.elements.queryInput.focus();
            });
        });

        // Check health on load
        this.checkHealth();
    }

    async checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();

            if (data.ready) {
                this.updateStatus('ready', `Ready (${data.provider})`);
                this.elements.providerInfo.textContent = `${data.provider} • ${data.model}`;
                this.currentProvider = data.provider;
                this.currentModel = data.model;
                this.defaultModels.openrouter = data.default_openrouter_model;
                this.defaultModels.ollama = data.default_ollama_model;

                // Initialize provider dropdown to current provider
                if (this.elements.providerSelect) {
                    this.elements.providerSelect.value = data.provider;
                }

                // Load models for current provider
                this.handleProviderChange(data.provider);
            } else {
                this.updateStatus('error', 'Not Ready');
                this.elements.providerInfo.textContent = 'Configuration Error';
            }
        } catch (error) {
            this.updateStatus('error', 'Connection Error');
            this.elements.providerInfo.textContent = 'Unable to connect';
            console.error('Health check failed:', error);
        }
    }

    async loadModels() {
        if (!this.elements.modelSelect) return;

        try {
            const response = await fetch('/api/models');
            if (!response.ok) {
                console.warn('Failed to load models:', response.status);
                return;
            }

            const models = await response.json();

            this.updateDefaultModelLabel(this.currentProvider);

            // Clear existing dynamic options (keep the default first option)
            this.elements.modelSelect.length = 1;

            models.forEach(model => {
                const option = document.createElement('option');
                const promptPrice = model.prompt_price_per_million;
                const completionPrice = model.completion_price_per_million;
                option.value = model.id;
                option.textContent = `${model.name} ($${promptPrice.toFixed(2)}/M in, $${completionPrice.toFixed(2)}/M out)`;
                this.elements.modelSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading models:', error);
        }
    }

    async loadOllamaModels() {
        if (!this.elements.modelSelect) return;

        try {
            const response = await fetch('/api/ollama/models');
            if (!response.ok) {
                console.warn('Failed to load Ollama models:', response.status);
                return;
            }

            const models = await response.json();

            this.updateDefaultModelLabel(this.currentProvider);

            // Clear existing dynamic options (keep the default first option)
            this.elements.modelSelect.length = 1;

            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.model || model.name;
                option.textContent = model.name;
                this.elements.modelSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading Ollama models:', error);
        }
    }

    handleProviderChange(provider) {
        this.currentProvider = provider;

        // Reset model selection to default
        if (this.elements.modelSelect) {
            this.elements.modelSelect.value = '';
        }

        this.updateDefaultModelLabel(provider);

        if (provider === 'openrouter') {
            this.loadModels();
        } else if (provider === 'ollama') {
            this.loadOllamaModels();
        }
    }

    updateDefaultModelLabel(provider) {
        if (!this.elements.modelSelect || this.elements.modelSelect.options.length === 0) {
            return;
        }

        const defaultName = this.defaultModels[provider];
        this.elements.modelSelect.options[0].textContent = defaultName
            ? `Default (${defaultName})`
            : 'Default (from config.yaml)';
    }

    updateStatus(status, text) {
        this.elements.statusText.textContent = text;
        this.elements.statusDot.className = `status-dot ${status}`;
    }

    getSelectedOutputFormat() {
        for (const radio of this.elements.outputFormatRadios) {
            if (radio.checked) {
                return radio.value;
            }
        }
        return 'mla';
    }

    async handleSubmit() {
        const query = this.elements.queryInput.value.trim();
        
        if (!query) {
            alert('Please enter a question');
            return;
        }

        if (this.isProcessing) {
            return;
        }

        this.isProcessing = true;
        this.setLoadingState(true);

        const stream = this.elements.streamCheckbox.checked;
        const outputFormat = this.getSelectedOutputFormat();
        const selectedModel = this.elements.modelSelect ? this.elements.modelSelect.value : '';

        try {
            if (stream) {
                await this.handleStreamingQuery(query, outputFormat, selectedModel);
            } else {
                await this.handleNonStreamingQuery(query, outputFormat, selectedModel);
            }
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.isProcessing = false;
            this.setLoadingState(false);
        }
    }

    async handleStreamingQuery(query, outputFormat, selectedModel) {
        this.clearResponse();
        this.updateStatus('processing', 'Streaming...');

        const responseDiv = document.createElement('div');
        responseDiv.className = 'response-content streaming';
        this.elements.responseContainer.appendChild(responseDiv);

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    stream: true,
                    output_format: outputFormat,
                    provider: this.currentProvider,
                    // Only send model when using a provider that supports selection
                    model: selectedModel || null,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep the last incomplete line

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.error) {
                                throw new Error(data.error);
                            }
                            
                            if (data.done) {
                                this.updateStatus('ready', 'Complete');
                                continue;
                            }
                            
                            if (data.chunk) {
                                responseDiv.textContent += data.chunk;
                                // Auto-scroll to bottom
                                this.elements.responseContainer.scrollTop = 
                                    this.elements.responseContainer.scrollHeight;
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
            }

            // Format the response if it's JSON
            if (outputFormat === 'json') {
                try {
                    const jsonObj = JSON.parse(responseDiv.textContent);
                    responseDiv.innerHTML = `<pre class="json-response">${JSON.stringify(jsonObj, null, 2)}</pre>`;
                } catch (e) {
                    // If not valid JSON, keep as is
                }
            } else {
                // Format as markdown-like for MLA
                this.formatResponse(responseDiv);
            }

        } catch (error) {
            throw new Error(`Streaming error: ${error.message}`);
        }
    }

    async handleNonStreamingQuery(query, outputFormat, selectedModel) {
        this.clearResponse();
        this.updateStatus('processing', 'Processing...');

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    stream: false,
                    output_format: outputFormat,
                    provider: this.currentProvider,
                    // Only send model when using a provider that supports selection
                    model: selectedModel || null,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Request failed');
            }

            const data = await response.json();
            
            const responseDiv = document.createElement('div');
            responseDiv.className = 'response-content';
            
            if (data.output_format === 'json') {
                try {
                    const jsonObj = JSON.parse(data.response);
                    responseDiv.innerHTML = `<pre class="json-response">${JSON.stringify(jsonObj, null, 2)}</pre>`;
                } catch (e) {
                    responseDiv.textContent = data.response;
                }
            } else {
                responseDiv.textContent = data.response;
                this.formatResponse(responseDiv);
            }
            
            this.elements.responseContainer.appendChild(responseDiv);
            this.updateStatus('ready', 'Complete');

        } catch (error) {
            throw new Error(`Query error: ${error.message}`);
        }
    }

    formatResponse(element) {
        // Simple markdown-like formatting for MLA responses
        let html = element.textContent;

        // Convert "Works Cited" section
        html = html.replace(/^Works Cited$/gm, '<h2>Works Cited</h2>');
        
        // Convert citations (lines starting with ")
        html = html.replace(/^"([^"]+)"/gm, '<p style="margin-left: 2rem; text-indent: -2rem;">"$1"</p>');
        
        // Convert paragraphs
        const lines = html.split('\n');
        let formatted = '';
        let inParagraph = false;
        
        for (let line of lines) {
            line = line.trim();
            if (line === '') {
                if (inParagraph) {
                    formatted += '</p>';
                    inParagraph = false;
                }
            } else if (line.startsWith('<h2>') || line.startsWith('<p style=')) {
                if (inParagraph) {
                    formatted += '</p>';
                    inParagraph = false;
                }
                formatted += line;
            } else {
                if (!inParagraph) {
                    formatted += '<p>';
                    inParagraph = true;
                } else {
                    formatted += ' ';
                }
                formatted += line;
            }
        }
        
        if (inParagraph) {
            formatted += '</p>';
        }
        
        element.innerHTML = formatted;
    }

    showError(message) {
        this.clearResponse();
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<strong>Error:</strong> ${message}`;
        this.elements.responseContainer.appendChild(errorDiv);
        this.updateStatus('error', 'Error');
    }

    clearResponse() {
        this.elements.responseContainer.innerHTML = '';
    }

    setLoadingState(loading) {
        this.elements.submitBtn.disabled = loading;
        const btnText = this.elements.submitBtn.querySelector('.btn-text');
        const btnLoading = this.elements.submitBtn.querySelector('.btn-loading');
        
        if (loading) {
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
        } else {
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
        }
    }
}

// Initialize the UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new WikipediaAgentUI();
});
