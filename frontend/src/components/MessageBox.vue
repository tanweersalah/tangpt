<template>
  <div>
    <q-icon class="box-icon" :name="icon" :color="icon_color" />
    <p>{{ text }}</p>
  </div>
</template>

<script>
export default {
  props: ["text", "icon", "icon_color"],
};
</script>

<style scoped>
div {
  width: 200px;
  display: flex;
  flex-direction: column;
  border: 1px solid grey;
  justify-content: center;
  padding: 10px;
  gap: 5px;
  border-radius: 20px;
  color: grey;
}
.box-icon {
  align-self: center;
}
p {
  justify-self: end;
  text-align: center;
}
</style>
