<script setup lang="ts">
import { useForm } from "vee-validate";
import * as yup from "yup";
import { push } from "notivue";
// SHADCN COMPONENTS
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import { SelectItem } from "@/components/ui/select";
// CUSTOM COMPONENTS
import TextField from "@/components/form/TextField.vue";
import SelectField from "@/components/form/SelectField.vue";
import TextAreaField from "@/components/form/TextAreaField.vue";
// STORE
import { useContact } from "@/stores/contact";

const { sendContactMessage } = useContact();

const validationSchema = yup.object({
  name: yup.string().required("Name is required"),
  email: yup.string().required("Email is required").email("Invalid email"),
  subject: yup.string().required("Subject is required"),
  reason: yup.string().required("Reason is required"),
  message: yup.string().required("Message is required")
});

const { handleSubmit, isSubmitting } = useForm({
  validationSchema,
  initialValues: { name: "", email: "", subject: "", reason: "", message: "" }
});

const onSubmit = handleSubmit(async (values, { resetForm }) => {
  try {
    await sendContactMessage(values);
    resetForm();
    push.success("Your message has been sent successfully");
  } catch (error) {
    console.log(error);
    push.error("Something went wrong, please try again");
  }
});
</script>

<template>
  <Card class="p-6 xl:py-8 mt-7">
    <div class="max-w-(--breakpoint-lg) mx-auto">
      <CardTitle class="text-base">Contact Us</CardTitle>
      <p class="text-muted font-normal text-sm mt-1 mb-6">
        Send us a message and our team will get back to you as soon as possible.
      </p>

      <CardContent>
        <form @submit="onSubmit" class="pt-2">
          <div class="grid grid-cols-12 gap-6">
            <div class="col-span-full md:col-span-6">
              <TextField id="name" name="name" label="Name" placeholder="Full Name" />
            </div>

            <div class="col-span-full md:col-span-6">
              <TextField id="email" name="email" label="Email" placeholder="Email" />
            </div>

            <div class="col-span-full md:col-span-6">
              <TextField id="subject" name="subject" label="Subject" placeholder="Subject" />
            </div>

            <div class="col-span-full md:col-span-6">
              <SelectField id="reason" name="reason" label="Reason" placeholder="Select a reason">
                <SelectItem value="general">General Inquiry</SelectItem>
                <SelectItem value="billing">Billing</SelectItem>
                <SelectItem value="technical">Technical Support</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectField>
            </div>

            <div class="col-span-full">
              <TextAreaField
                id="message"
                name="message"
                label="Message"
                placeholder="Write your message" />
            </div>
          </div>

          <Button type="submit" class="px-8 mt-8" :disabled="isSubmitting">Submit</Button>
        </form>
      </CardContent>
    </div>
  </Card>
</template>
