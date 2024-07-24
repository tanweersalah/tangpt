<template>
  <main class="home-container">
    <div class="q-pa-m">
      <q-layout
        view="hHh Lpr lff"
        
        class="shadow-2 rounded-borders"
      >
        <q-header elevated class="bg-black">
          <q-toolbar>
            <q-btn flat @click="drawer = !drawer" round dense icon="menu" />
            <q-toolbar-title>TanGPT</q-toolbar-title>
          </q-toolbar>
        </q-header>

        <q-drawer
          v-model="drawer"
          show-if-above
          :width="200"
          :breakpoint="500"
          bordered
          class="bg-grey-9"
        >
        <!-- <q-btn label="Scroll to bottom" color="primary" @click="scrollToBottom" ></q-btn> -->
          <q-scroll-area class="fit">
            <q-list>
              <template v-for="(menuItem, index) in menuList" :key="index">
                <q-item
                  clickable
                  :active="menuItem.label === 'Outbox'"
                  v-ripple
                >
                  <q-item-section avatar>
                    <q-icon :name="menuItem.icon" />
                  </q-item-section>
                  <q-item-section>
                    {{ menuItem.label }}
                  </q-item-section>
                </q-item>
                <q-separator :key="'sep' + index" v-if="menuItem.separator" />
              </template>
            </q-list>
          </q-scroll-area>
        </q-drawer>

        <q-page-container class="page-content">
          <div class="chat-window">
            
            <div class="q-pa-md row justify-center">
              
              <q-scroll-area class="fit" style="width: 100%"  ref="chatScroll">
                <div v-for="(message,index) in messages" :key="index"> 
                <q-chat-message v-if="message['type']==='user'"
                  name="me"
                  
                  
                  sent
                  text-color="white"
                  bg-color="primary"
                >
                  <div>{{message['message']}}</div>

                  </q-chat-message>

                <q-chat-message v-if="message['type']==='gpt'" 
                  name="TanGPT"
                  avatar="https://geeksgod.com/wp-content/uploads/2021/05/Logopit_1603470318463-300x300.png"
                  
                  text-color="black"
                >
                <div v-html='message["message"]' />
                  <!-- <q-spinner-dots size="2rem" /> -->
                </q-chat-message>
                

                </div>
                <q-chat-message v-if='message_procession'  
                  name="TanGPT"
                  avatar="https://geeksgod.com/wp-content/uploads/2021/05/Logopit_1603470318463-300x300.png"
                  bg-color="green"
                >
                
                  <q-spinner-dots size="2rem" />
                </q-chat-message>
                <q-scroll-observer />
              </q-scroll-area>
            </div>

            <div class="chat-text-box">
              <q-input
                rounded
                outlined
                dense
                autogrow
                class="chat-input"
                bg-color="grey"
                v-model="message"
                placeholder="Type a message"
              >
                <template v-slot:append>
                  <q-avatar @click="get_response(message)">
                    <img src="https://cdn.quasar.dev/logo-v2/svg/logo.svg" />
                  </q-avatar>
                </template>
              </q-input>
            </div>
          </div>
        </q-page-container>
      </q-layout>
    </div>
  </main>
</template>

<script>
import { inject, ref } from "vue";
import {marked} from 'marked';

const menuList = [
  {
    icon: "inbox",
    label: "Chat History",
    separator: true,
  },
];

export default {
 
  setup() {
    return {
      drawer: ref(false),
      menuList,
    };
  },
  created() {
    var uniqueId = this.generateUniqueId();

        // Store the new unique ID in session storage
        sessionStorage.setItem('uniqueId',uniqueId);
    
    console.log(uniqueId)
  },
  methods:{

    getUniqueId() {
    // Define the key used to store the unique ID in session storage
    const uniqueIdKey = 'uniqueId';

    // Check if the unique ID is already stored in session storage
    let uniqueId = sessionStorage.getItem(uniqueIdKey);

    // If the unique ID does not exist, generate a new one
    if (!uniqueId) {
        // Generate a new unique ID
        uniqueId = this.generateUniqueId();

        // Store the new unique ID in session storage
        sessionStorage.setItem(uniqueIdKey, uniqueId);
    }

    // Return the unique ID
    return uniqueId;
},

// Helper function to generate a new unique ID
 generateUniqueId() {
    // You can use any unique ID generation logic here
    // This example uses a combination of the current timestamp and a random number
    return 'id-' + Date.now() + '-' + Math.floor(Math.random() * 10000);
},
    scrollToBottom() {
      const scrollArea = this.$refs.chatScroll;
      if (scrollArea && scrollArea.$el) {
        const scrollElement = scrollArea.$el.querySelector('.q-scrollarea__container');
        if (scrollElement) {
          scrollElement.scrollTop = scrollElement.scrollHeight;
        }
      }
    }

    
  ,
    async get_response(text){
      var u_id = this.getUniqueId()
      console.log(u_id)
      this.messages.push({"type": "user", "message":text});
      this.message_procession = true
      setTimeout(() => {
    this.scrollToBottom();
}, 200);
      var new_message = await this.backend.getGptResponse(text, u_id);
      this.message_procession = false
      
      

      console.log(new_message)
      var html_msg = this.renderedMarkdown(new_message);
      this.messages.push({"type": "gpt", "message":html_msg});
      setTimeout(() => {
    this.scrollToBottom();
}, 1000);
      
    },
    renderedMarkdown(text) {
      return marked(text);
    }},
  
  
  data(){
    return {
      backend : inject('backendService'),
      messages : [],
      message_procession : false,
      scrollsize: 0,
    }
  }
};
</script>

<style scoped>
.page-content {
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;

}
.chat-window {
  
  max-width: 1200px;
  font-size: 1.1rem;
  display: grid;
  grid-template-rows: auto 70px;
  height: 100%;
  width: 100%;
}
.chat-text-box {
  align-self: center;
  padding-left: 20px;
  padding-right: 20px;
}
.chat-input {
  width: 100%;
}

.home-container {
  height: 100%;
  width: 100vw;
}

.chat-history {
  background-color: rgb(38, 56, 50);
}

.chat-container {
  background-color: aquamarine;
}
</style>

<style lang="sass">
.my-emoticon
  vertical-align: middle
  height: 2em
  width: 2em
</style>
