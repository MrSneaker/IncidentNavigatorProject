var nbAssistMsg = 0;
var context = new Array();
let initDone = false;
let contextSize = 0;
let nbToken = 0;
let btnEnabled = true;
let maxToken = 2000;
let domain = window.location.origin;
let paramView, paramExist = false;
let settingsTemp = 1;
let promptData;
let userRef;

let copyBtnValue = "Copy";
let copyBtnLabel = "Copy";
let includeBtnValue = "Include";
let includeBtnLabel = "Include";
let assistInfoName = "Assistant";
let editButtonValue;
let editButtonLabel;
let settingsTitle;
let sliderLabel;
let sysPrptDisLabel;
let userPrptDisLabel;

// controler to stop a request if needed.
let globalAbortController = new AbortController();
let globalSignal = globalAbortController.signal;

/**
 *
 * Scroll to the bottom of the chat box when called.
 *
 */
function scrollToBottom() {
    const chatContent = document.querySelector('#chatContent');
    chatContent.scrollTop = chatContent.scrollHeight;
}

/**
 *
 * @param {HTMLElement} obj A text area.
 * This is used to resize the user input area.
 *
 */
function autoResizeInput(obj) {
    let scrollHeight = obj.scrollHeight;
    let nbChar = obj.value.length;
    if (scrollHeight < 100) { // min height of 100px
        obj.style.height = '4em';
    } else if (scrollHeight > 200) { // max height 200px
        obj.style.height = '190px';
        obj.style.overflowY = 'auto';
        obj.scrollHeight = obj.scrollHeight - 5;
    } else {
        let nbPx = (nbChar / 66) * 18;
        if (nbPx > 100)
            nbPx = 100;
        else if (nbPx > 200)
            nbPx = 200;
        obj.style.height = nbPx + 'px';
    }
    if (nbChar == 0) {
        console.log('00!')
        obj.style.height = '4em';
    }

}

/**
 * *
 * Attach an event listener to the user text input area to enable auto resizing. 
 *
 */
function handleAutoResizeInput() {
    let textarea = document.querySelector('#txt-input');
    textarea.addEventListener('input', (event) => {
        autoResizeInput(textarea);
    });
    autoResizeInput(textarea);
}


/**
 *
 * @param {string} str A string representation of a json.
 * @return true if the string in parameter is valid JSON, else return false.
 *
 */
function isJSON(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}


/**
    *
    * @param {string} userChat The user input.
    * @return {HTMLPreElement} An HTML representation of the user chat.
    *
    */
function addUserChat(userChat) {
    const preElement = document.createElement('pre');
    preElement.classList.add('user-message');

    const msgInfo = document.createElement('div');
    msgInfo.classList.add('msg-info');
    msgInfo.textContent = 'User';
    preElement.appendChild(msgInfo);

    const userMessage = document.createElement('div');
    userMessage.id = `user-content-${nbAssistMsg}`;
    userMessage.textContent = userChat;
    preElement.appendChild(userMessage);

    const userMsgButtons = document.createElement('div');
    userMsgButtons.classList.add('msgButtonWrapper');

    // const msgBtn = document.createElement('button');
    // msgBtn.classList.add('userMsgButton');
    // msgBtn.type = 'button';
    // msgBtn.id = `user-btn-${nbAssistMsg}`;
    // msgBtn.title = editButtonLabel;
    // msgBtn.textContent = editButtonValue;
    // userMsgButtons.appendChild(msgBtn);
    // preElement.appendChild(userMsgButtons);

    return preElement;
}


/**
  * @param {string} assistantChat The LLM AI answer.
  * @param {number} elapsedTime The time elapsed between the user chat and this answer in seconde.
  * @return {HTMLDivElement} An HTML representation of the LLM AI answer.
  *
  */
function addAssistantChat(assistantChat, elapsedTime) {
    nbAssistMsg++;
    const div = document.createElement('div');
    div.id = `assist-msg-${nbAssistMsg}`;
    div.classList.add('assistant-message');

    const modelInfo = document.createElement('div');
    modelInfo.classList.add('msg-info');
    modelInfo.id = `mod-inf-${nbAssistMsg}`;
    if (paramView) {
        modelInfo.textContent = `${assistInfoName} (model-name) - ${elapsedTime} sec - T: ${settingsTemp}`;
    }
    else {
        modelInfo.textContent = `${assistInfoName} (model-name)) - ${elapsedTime} sec`;
    }
    div.appendChild(modelInfo);

    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');
    messageContent.id = `msg-content-${nbAssistMsg}`;
    messageContent.innerHTML = marked.parse(assistantChat);;
    div.appendChild(messageContent);

    const astMsgButton = document.createElement('div');
    astMsgButton.classList.add('astMsgButtonWrapper');

    const copyButton = document.createElement('button');
    copyButton.type = 'button';
    copyButton.classList.add('copy-button');
    copyButton.id = `copy-button-${nbAssistMsg}`;
    copyButton.style.display = 'none';
    copyButton.title = copyBtnLabel;
    copyButton.textContent = copyBtnValue;
    astMsgButton.appendChild(copyButton);

    const includeButton = document.createElement('button');
    includeButton.type = 'button';
    includeButton.classList.add('include-button');
    includeButton.id = `include-button-${nbAssistMsg}`;
    includeButton.style.display = 'none';
    includeButton.title = includeBtnLabel;
    includeButton.textContent = includeBtnValue;
    astMsgButton.appendChild(includeButton);

    div.appendChild(astMsgButton);

    return div;
}


/**
    *
    * @param {string} msg The message to display.
    * @param {string} link The link to redirect to (can be set to null)
    * @param {string} linkText The label to display for the link (can be null).
    * @return {HTMLDivElement} An HTML representation of the system chat.
    *
    */
function addSystemChat(msg, link, linkText) {
    const divElement = document.createElement('div');
    divElement.id = 'system-msg';
    divElement.classList.add('system-message');

    const systemInfo = document.createElement('div');
    systemInfo.classList.add('msg-info');
    systemInfo.textContent = 'System';
    divElement.appendChild(systemInfo);

    const messageContent = document.createElement('pre');
    messageContent.classList.add('message-content');
    messageContent.textContent = msg;
    divElement.appendChild(messageContent);

    const htmlLink = document.createElement('a');
    htmlLink.href = link;
    htmlLink.textContent = linkText;
    divElement.appendChild(htmlLink);

    return divElement;
}


/**
  *
  * @param {HTMLElement} chatContent The current chat window of the interface.
  * @return {HTMLDivElement} An HTML representation of the loading animation.
  *
  */
function addLoading(chatContent) {
    chatContent.innerHTML += `<div class="waiting-line">
                                <div class="dot dot1"></div>
                                <div class="dot dot2"></div>
                                <div class="dot dot3"></div>
                            </div>`;
    scrollToBottom();
}

/**
 *
 * Remove the last Loading animation added from the chat.
 * @param {HTMLElement} chatContent The current chat window of the interface.
 *
 */
function removeLoading(chatContent) {
    const loadingLine = chatContent.querySelector('.waiting-line');
    if (loadingLine) {
        loadingLine.remove();
    }
}

/**
 *
 * For streaming request, update the corresponding assistant chat with the new informations.
 * @param {number} msgIdNum The assistant chat ID to update.
 * @param {number} updatedTime The new time to display since the beginning of the interaction in seconde.
 * @param {string} chunkReply The chunk of the answer to add.
 * @param {string} model The LLM model answering.
 *
 */
function updateAssistantChat(msgIdNum, updatedTime, chunkReply, model) {
    if (paramView)
        document.querySelector('#mod-inf-' + msgIdNum).textContent = `${assistInfoName} (${model}) - ${updatedTime} sec - T: ${settingsTemp}`;
    else
        document.querySelector('#mod-inf-' + msgIdNum).textContent = `${assistInfoName} (${model}) - ${updatedTime} sec`;
    document.querySelector('#msg-content-' + msgIdNum).textContent += chunkReply;
}

/**
 *
 * @param {string} errorMessage The error message to display.
 * @return {HTMLDivElement} A div element containing the error message HTML representation.
 *
 */
function errorMessagePrint(errorMessage) {
    return `<div class="errorHandler">${errorMessage}</div>`;
}

/**
 * Change the interface button state based on their actual state.
 */
function changeBtnState() {
    if (btnEnabled) {
        document.querySelector('#subButton').disabled = true;
        // document.querySelector('#dropMenu').disabled = true;
        document.querySelector('#stopRqst').style.display = "block";
        btnEnabled = false;
    }
    else {
        document.querySelector('#subButton').disabled = false;
        // document.querySelector('#dropMenu').disabled = false;
        document.querySelector('#stopRqst').style.display = "none";
        btnEnabled = true;
    }
}


/**
  * Send the user chat to the model. Bind parameters to make the request.
  * @param {Event} event The sending event.
  * @param {HTMLFormElement} form The form element of the interface.
  */
function submitChat(event, form) {
    event.preventDefault(); // Prevent the form from submitting normally
    // Get the text from the textarea
    const userText = form.elements.input.value;
    if (userText === "") {
        alert("Your request is empty, please write an input.");
        return false;
    }

    // Adding the user chat in the page
    const chatContent = document.querySelector('#chatContent');
    // if (promptData.prompt !== '') {
    //     if (paramView)
    //         chatContent.appendChild(addSystemChat('The prompt used is: ' + promptData.prompt + ' With a custom temperature of ' + settingsTemp + '.'));
    //     else
    //         chatContent.appendChild(addSystemChat('The prompt used is: ' + promptData.prompt));
    // }
    chatContent.appendChild(addUserChat(userText));
    scrollToBottom();
    // chatContent.appendChild(addAssistantChat('test', 'nom-modele', 0.0));

    const params = getRequestParams(userText, promptData.prompt, context, settingsTemp);
    const options = getRequestOptions(params);

    console.log(params)
    console.log(options)

    // // Make the POST request with query parameters
    postRequest(options, chatContent, userText);
    document.querySelector('#txt-input').style.height = '100px';
}

/**
 * Method called to make every request to the models.
 * @param {JSON} options The JSON representation of the request options. 
 * @param {HTMLElement} chatContent The chat box element.
 * @param {string} userText The user text corresponding to this request.
 * @param {boolean} isStreaming true if the request can be streamed, else false.
 */
function postRequest(options, chatContent, userText) {
    changeBtnState();
    document.querySelector('#txt-input').value = '';
    const URI = "/rest/v1/chat/completions";
    const start = Date.now();
    console.log('context before stream req : ', context[contextSize])
    streamingRequest(chatContent, URI, options, start, userText);

}

/**
 * /!\ This method is extremely approximative and need to be change with appropriate tokenizer.
 * Manage the context size based on the number of token and the maximum token usable.
 */
function tokenManager() {
    nbToken += countTokens(context[contextSize]);
    contextSize++;
    // Manage the number of token so the request is not too long.
    let ind = 0;
    while (nbToken > maxToken) {
        nbToken -= countTokens(context[ind]);
        context.shift();
        ind++;
    }
}

/**
 * /!\ This method is extremely approximative and need to be change with appropriate tokenizer.
 * @param {JSON} query A json representation of the last context.
 * @return {number} The number of token from the specified query.
 */
function countTokens(query) {
    let strContext;
    strContext += query.user;
    strContext += query.assistant;
    strContext.trim();
    const words = strContext.split(' ');
    const filteredWords = words.filter(word => word !== '');
    // One token equal to approximatively 1.3 token (based on OpenAI tokenization)
    const tokenCount = filteredWords.length * 1.3;
    return Math.floor(tokenCount);
}


/**
 * Initialize the stream request.
 * @param {HTMLElement} chatContent The chat box element.
 * @param {string} URI The URI where the request has to be sent. 
 * @param {JSON} options The JSON representation of the request options. 
 * @param {number} startTime The Date in ms the assistant started writing.
 * @param {string} userText The user text corresponding to this request.
 */
function streamingRequest(chatContent, URI, options, startTime, userText) {
    addLoading(chatContent);
    fetch(URI, options).then((response) => {
        const reader = response.body.getReader();
        return new ReadableStream({
            start(controller) {
                function push() {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            controller.close();
                            return;
                        }
                        const chunk = new TextDecoder().decode(value);
                        controller.enqueue(chunk);
                        push();
                    });
                }
                push();
            }
        });
    }).then((stream) => {
        return streamResponse(chatContent, stream, startTime, userText);
    }).catch((error) => {
        if (error.name !== 'AbortError') {
            console.error('Error:', error);
            errorCatcher(chatContent, error);
            changeBtnState();
            removeLoading(document.querySelector('#chatContent'));
        }
    });
}

/**
     * Handle a chunk of reply comming from the stream communication with the LLM model.
     * @param {string} jsonMessages The string representation of the chunk of the reply to treat.
     * @param {string} completedReply The string containing the full reply until now.
     * @param {boolean} beginRep State if the answer already started or not. 
     * @param {boolean} isErr State if the chunk received is an error or not. 
     * @param {string} model The LLM model name.
     * @param {number} startTime The Date in ms the assistant started writing.
     * @return {JSON} A JSON object containing the updated state of isErr, beginRep, and completedReply.
     */
function handleValidChunk(jsonMessages, completedReply, beginRep, isErr, startTime) {
    for (const jsonMessage of jsonMessages) {
        if (jsonMessage.trim() !== '') {
            console.log(jsonMessage)
            const message = JSON.parse(jsonMessage);
            let reply = '';
            // Extract the generated reply from the response
            if (message.choices[0].finish_reason !== 'stop') {
                reply = message.choices[0].delta.content;
            }

            // Handle the generated reply as desired
            if (reply) {
                completedReply += reply;
                if (beginRep) {
                    initChatOnStream(chatContent);
                    beginRep = false;
                }
                const elapsedTime = (Date.now() - startTime) / 1000;
                updateAssistantChat(nbAssistMsg, elapsedTime, reply);
            }

        }
    }
    return { isErr, beginRep, completedReply };
}

/**
 * Init the new chat that begin to be received.
 * @param {HTMLElement} chatContent The chat box element.
 * @param {string} model The LLM model name.
 */
function initChatOnStream(chatContent) {
    removeLoading(chatContent);
    chatContent.appendChild(addAssistantChat('', 0));
    scrollToBottom();
}

/**
 * Update the chat information in the back (number of token and context) at the end of the stream communication.
 * @param {string} completedReply The full reply at the end of the communication.
 */
function updateChatOnStream(completedReply) {
    context[contextSize].assistant = completedReply;
    document.querySelector('#msg-content-' + nbAssistMsg).innerHTML = marked.parse(completedReply);
    tokenManager();
    scrollToBottom();
}

/**
 * Process the stream request and update the interface along.
 * @param {Object} obj An object with 'done' and 'value'. 'done' is a boolean true if the request has ended, else false. 'value' is the last string value communicated.
 * @param {HTMLElement} chatContent The chat box element.
 * @param {string} completedReply The string containing the full reply until now.
 * @param {string} accumulatedChunks The string containing every json representation of the received chunk.
 * @param {string} isErr State if the chunk received is an error or not. 
 * @param {string} beginRep State if the answer already started or not. 
 * @param {any} reader The reader used to read the stream.
 * @param {number} startTime The Date in ms the assistant started writing.
 * @param {string} userText The user text corresponding to this request.
 */
function processStream({ done, value }, chatContent, completedReply, accumulatedChunks, isErr, beginRep, reader, startTime, userText) {
    try {
        if (done) {
            if (!isErr) {
                const copyBtn = document.querySelector('#copy-button-' + nbAssistMsg);
                const includeBtn = document.querySelector('#include-button-' + nbAssistMsg);
                if (copyBtn && includeBtn) {
                    context.push({ user: userText });
                    copyBtn.style.display = "block";
                    includeBtn.style.display = "block";
                    updateChatOnStream(completedReply);
                }
                else {
                    throw new Error('The model finished without responding. Please make sure the model can be loaded correctly on the server side. The server may have run out of capacity while running the model.');
                }
            }
            else {
                if (isJSON(accumulatedChunks)) {
                    let message = JSON.parse(accumulatedChunks);
                    errorCatcher(chatContent, message.error);
                    removeLoading(chatContent);
                }
            }
            changeBtnState();
            return;
        }
        else {
            accumulatedChunks += value;
            // Extract complete JSON messages
            let jsonMessages;
            let isValidChunk = true;
            if (accumulatedChunks.indexOf('data: ') !== -1) {
                jsonMessages = accumulatedChunks.split('data: ').filter(Boolean);
            }
            else {
                isValidChunk = false;
            }
            // Process complete JSON messages
            if (isValidChunk) {
                accumulatedChunks = jsonMessages.pop(); // Keep the incomplete message for the next iteration
                ({ isErr, beginRep, completedReply } = handleValidChunk(jsonMessages, completedReply, beginRep, isErr, startTime));
                return reader.read().then(value =>
                    processStream(value, chatContent, completedReply, accumulatedChunks, isErr, beginRep, reader, startTime, userText));
            }
            else
                return reader.read().then(value =>
                    processStream(value, chatContent, completedReply, accumulatedChunks, true, beginRep, reader, startTime, userText));
        }
    } catch (error) {
        console.error('error stream : ', error);
        errorCatcher(chatContent, error);
        removeLoading(chatContent);
        changeBtnState();
    }

}

/**
 * Set up the start of the process for the streaming response of the LLM model.
 * @param {HTMLElement} chatContent The chat box element.
 * @param {Object} stream The actual stream object.
 * @param {number} startTime The Date in ms the assistant started writing.
 * @param {string} userText The user text corresponding to this request.
 */
function streamResponse(chatContent, stream, startTime, userText) {
    const reader = stream.getReader();
    let accumulatedChunks = '';
    let completedReply = '';
    let isErr = false;
    let beginRep = true;

    return reader.read().then(value =>
        processStream(value, chatContent, completedReply, accumulatedChunks, isErr, beginRep, reader, startTime, userText));
}

/**
 * Add an error message to the chat box.
 * @param {HTMLElement} chatContent The chat box element.
 * @param {JSON} error The JSON object containing error information. 
 */
function errorCatcher(chatContent, error) {
    chatContent.innerHTML += errorMessagePrint("An error occured: " + error.message);
}


/**
 * Build the parameters to send for the request.
 * @param {string} userText The user chat input.
 * @param {string} prompt The system prompt to send.
 * @param {string} context The previous context of the conversation.
 * @param {number} temp The temperature of the chat.
 * @return {JSON} A JSON representation of the parameters.
 */
function getRequestParams(userText, prompt, context, temp) {

    console.log('context used to make param : ', context)

    const params = {
        text: userText,
        context: context,
        prompt: prompt,
        temperature: Number(temp),
        stream: "true",
    };
    return params;
}

/**
 * Build the options for the fetch request to the API.
 * @param {JSON} params The body of the request, can be set to null.
 * @returns {JSON} A JSON representation of the request options. 
 */
function getRequestOptions(params) {
    const options = {
        method: 'POST',
        body: JSON.stringify(params),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + sessionStorage.getItem('jwt')
        },
        signal: globalSignal
    };
    return options;
}

/**
 * Method used to abort the ongoing request.
 */
function abortRequest() {
    globalAbortController.abort();
    const chatContent = document.querySelector('#chatContent');
    chatContent.appendChild(addSystemChat("You aborted the ongoing request."));
    removeLoading(chatContent);
    scrollToBottom();
    changeBtnState();
    // reset the signal
    globalAbortController = new AbortController();
    globalSignal = globalAbortController.signal;
}

/**
 * Initialize form event.
 * @param {HTMLFormElement} form The form HTML element of the interface.
 */
function initFormEvent(form) {
    // Add an event listener to the form submit event
    const subBtn = document.querySelector('#subButton');
    subBtn.addEventListener('click', (event) => {
        submitChat(event, form)
    });

    // const newConvButton = document.querySelector('#newconv');
    // newConvButton.addEventListener('click', (event) => {
    //     document.querySelector('#chatContent').innerHTML = '';
    //     nbAssistMsg = 0;
    //     context.splice(0, context.length);
    //     contextSize = 0;
    //     nbToken = 0;
    // });

    const stopRqstButton = document.querySelector('#stopRqst');
    stopRqstButton.addEventListener('click', (event) => {
        abortRequest();
    });

    promptData = { prompt: '', temperature: 1 };
}


/**
 *  Initialize the LLM extension.
 */
async function init() {
    if (initDone)
        return;
    initDone = true;
    // Select the form element
    const form = document.querySelector('#userChat');
    if (!form) {
        console.error("Failed to initialize because it could not find the #userChat form");
        return;
    }
    Promise.all([initFormEvent(form)])
        .then((res) => {
            if (res[2])
                setTimeout(() => {
                    document.querySelector('#chatContent').innerHTML = '';
                    changeBtnState();
                }, 2000);
        });
    handleAutoResizeInput();
}

init();