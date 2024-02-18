import './App.css';
import "./normal.css"


function App() {

  async function handleSubmit(e) {
    e.preventDefault();
    console.log("submit")
  }

  return (
    <div className="App">
    <aside className="sidemenu">
      <div className="side-menu-button">
        <span>
          +
        </span>
        New Chat
      </div>
    </aside>
    <section className="chatbox">
      <div className="chat-log">
        <div className="chat-message">
          <div className="chat-message-center">
            <div className="avatar">
            
            </div>
            <div className="message">
              Hello
            </div>
          </div>
        </div>
        <div className="chat-message chatgpt">
          <div className="chat-message-center">
            <div className="avatar chatgpt">
            
            </div>
            <div className="message">
              AI
            </div>
          </div>
        </div>
      </div>
    <div className="chat-input-holder"> 
      <form onSubmit={handleSubmit}>
        <input rows="1" className="chat-input-area" placeholder="Type your message here">
        </input>
      </form>
    </div>
    </section>
    </div>
  );
}

export default App;
