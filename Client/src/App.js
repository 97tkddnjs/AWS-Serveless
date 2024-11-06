import React, { Component } from 'react';
import styles from "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import axios from 'axios';
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
} from "@chatscope/chat-ui-kit-react";
import { Map, List, Record } from 'immutable';
import moment from 'moment';

const API_GATEWAY_ID = PROCESS.env.API_GATEWAY_ID
const SOCKET_API_GATEWAY_ID = PROCESS.env.SOCKET_API_GATEWAY_ID
class App extends Component {

  constructor(props) {
    super(props)
    this.state = {
      data: Map(
        {
          messageList: [],
          messages: []
        })
    }
    this.websocket = undefined;
    this.timer = undefined;
  }
  closeWebSocket = () => {

    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }
  connectToWebScoket = () => {
    const address = `wss://${SOCKET_API_GATEWAY_ID}.execute-api.ap-northeast-2.amazonaws.com/dev?room_id=test`
    this.websocket = new WebSocket(address);

    this.websocket.onopen = (data) => {

      console.log("open===",data)
      this.timer = setInterval(() => {
        this.websocket.send(JSON.stringify({ message: 'ping' }));
      }, 60 * 1000);
    };

    this.websocket.onmessage = (message) => {
      console.log('web socket ',message.data)
      let obj = JSON.parse(message.data);
      this.onMessageReceived(obj);



    };

    this.websocket.onclose = (event) => {
      console.log('onclose');
      if (this.timer || this.websocket) this.closeWebSocket();
    };

    this.websocket.onerror = (event) => {
      console.error('WebSocket error observed:', event);
      if (this.timer || this.websocket) this.closeWebSocket();
    };
  }
  componentDidMount = async () => {
    const { data } = this.state;
    const result = await axios({
      method: 'GET',
      url: `https://${API_GATEWAY_ID}.execute-api.ap-northeast-2.amazonaws.com/dev/chat?room_id=test`,
      params: {
        room_id: "test"
      }
    });;
    console.log('result : ', result.data.body)
    this.setState({
      data: data.set("messages", result.data.body).set("user_id", moment().valueOf())
    })

    this.connectToWebScoket();
  }
  onMessageReceived = async (message) => {
    console.log(' message : ', message)
    if (message.timestamp) {
      const { data } = this.state;
      let list = data.get("messages");
      list.push(message)
      console.log(list);
      this.setState({
        data: data.set("messages", list)
      })
    }
  }
  onSend = async (message) => {
    const { data } = this.state;
    const result = await axios({
      method: 'PUT',
      url: `https://${API_GATEWAY_ID}.execute-api.ap-northeast-2.amazonaws.com/dev/chat`,
      data: {
        room_id: "test",
        text: message,
        user_id: data.get("user_id"),
        name: "name_test"

      }
    });;
  }
  getMessageList = () => {

    const { data } = this.state;
    const userId = data.get("user_id");

    let messageList = [];
    console.log(` data  ${userId} :`,  data ,typeof data.get("messages") )
  
      data.get("messages").forEach((message) => {
        messageList.push(<Message
          key={message.timestamp}
          model={{
            message: message.message,
            sentTime: "just now",
            sender: "Joe",
            direction: (userId == message.user_id) ? "outgoing" : "not",
          }}
        />
        );
      })
    
    
    // messageList.push(<Message
    //   model={{
    //     message: "test",
    //     sentTime: "just now",
    //     sender: "Joe",
    //   }}
    // />
    // );
    // messageList.push(
    //   <Message model={{
    //     message: "Hello my friend",
    //     sentTime: "just now",
    //     sender: "Akane",
    //     direction: "outgoing",
    //     position: "single"
    //   }} />

    return messageList;

  }

  render() {

    return (

      // Your JSX...

      <div style={{ position: "relative", height: "500px" }}>
        <MainContainer>
          <ChatContainer>
            <MessageList>
              {this.getMessageList()}
            </MessageList>
            <MessageInput placeholder="Type message here" onSend={this.onSend} />
          </ChatContainer>
        </MainContainer>
      </div>

    )

  }
}

export default App;
