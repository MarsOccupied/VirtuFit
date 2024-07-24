import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as models
from torchvision.utils import save_image
import numpy as np

# A class to load a VGG19 model and extract features from specific layers.
class VGGNet(nn.Module):
    def __init__(self, style_layers, content_layers):
        super(VGGNet, self).__init__()
        self.chosen_features = style_layers + content_layers
        self.model = models.vgg19(pretrained=True).features
        self.model.eval() # Set to evaluation mode

    def forward(self, x):
        features = []
        for name, layer in self.model._modules.items():
            x = layer(x)
            if str(int(name) + 1) in self.chosen_features:
                features.append(x)
        return features

# Preprocessing for images
loader = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Un-processing for images (to display them)
unloader = transforms.Compose([
    transforms.Normalize(mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225], std=[1/0.229, 1/0.224, 1/0.225]),
    transforms.ToPILImage(),
])

def image_loader(image_name):
    image = Image.open(image_name).convert('RGB')
    image = loader(image).unsqueeze(0)
    return image.to(device, torch.float)

def tensor_to_pil(tensor):
    image = tensor.cpu().clone()
    image = image.squeeze(0)
    image = unloader(image)
    return image

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Gram matrix for style representation
def gram_matrix(input):
    a, b, c, d = input.size()  # a=batch size(=1)
    # b=number of feature maps
    # (c,d)=dimensions of a f. map (N=c*d)

    features = input.view(a * b, c * d)  # resise F_XL into \hat F_XL
    G = torch.mm(features, features.t())  # compute the gram product

    # we 'normalize' the values of the gram matrix
    # by dividing by the number of element in each feature maps.
    return G.div(a * b * c * d)

class StyleTransfer:
    def __init__(self, content_img_path, style_img_path, num_steps=300, style_weight=1e6, content_weight=1):
        self.content_img = image_loader(content_img_path)
        self.style_img = image_loader(style_img_path)
        self.input_img = self.content_img.clone()

        self.style_layers = ['1', '6', '11', '20', '29'] # These are approximate, need careful mapping to VGG19
        self.content_layers = ['22'] # Another approximate layer

        self.model = VGGNet(self.style_layers, self.content_layers).to(device)

        self.optimizer = optim.LBFGS([self.input_img.requires_grad_()]) # Use LBFGS for better results, but slower
        # self.optimizer = optim.Adam([self.input_img.requires_grad_()], lr=0.01) # Alternative for faster, but potentially lower quality

        self.num_steps = num_steps
        self.style_weight = style_weight
        self.content_weight = content_weight

    def train(self):
        run = [0]
        while run[0] <= self.num_steps:
            def closure():
                self.input_img.data.clamp_(0, 1)

                self.optimizer.zero_grad()

                content_features = self.model(self.content_img)
                style_features = self.model(self.style_img)
                input_features = self.model(self.input_img)

                style_loss = 0
                content_loss = 0

                for i, layer in enumerate(self.style_layers):
                    input_s = input_features[i]
                    style_s = style_features[i]
                    style_loss += torch.mean((gram_matrix(input_s) - gram_matrix(style_s))**2)

                for i, layer in enumerate(self.content_layers):
                    input_c = input_features[len(self.style_layers) + i]
                    content_c = content_features[len(self.style_layers) + i]
                    content_loss += torch.mean((input_c - content_c)**2)

                style_loss *= self.style_weight
                content_loss *= self.content_weight

                total_loss = style_loss + content_loss
                total_loss.backward()

                run[0] += 1
                if run[0] % 50 == 0:
                    print(f"run {run[0]}:")
                    print(f"Style Loss : {style_loss.item():4f} Content Loss: {content_loss.item():4f}")
                    print()

                return total_loss

            self.optimizer.step(closure)

        self.input_img.data.clamp_(0, 1)
        return tensor_to_pil(self.input_img)

# Placeholder for real-time application
def apply_style_to_frame(frame_np_array, style_image_path="python_core/style.jpg", num_steps_per_frame=2):
    # This function now performs a *very short* iterative style transfer on each frame.
    # This is intentionally very slow and highlights a major performance bottleneck
    # that will need to be addressed by using a pre-trained feed-forward network.

    pil_image = Image.fromarray(frame_np_array)
    content_tensor = loader(pil_image).unsqueeze(0).to(device, torch.float)

    # Load style image (can be optimized by loading once)
    style_tensor = image_loader(style_image_path)

    stylizer = StyleTransfer_Frame(content_tensor, style_tensor, num_steps=num_steps_per_frame)
    output_pil_image = stylizer.train()
    return np.array(output_pil_image)

class StyleTransfer_Frame(StyleTransfer):
    def __init__(self, content_tensor, style_tensor, num_steps=2, style_weight=1e6, content_weight=1):
        super(StyleTransfer_Frame, self).__init__(None, None, num_steps, style_weight, content_weight) # Pass None for paths
        self.content_img = content_tensor
        self.style_img = style_tensor
        self.input_img = self.content_img.clone()
        self.optimizer = optim.LBFGS([self.input_img.requires_grad_()]) # Use LBFGS for better results, but slower

if __name__ == '__main__':
    # This is for testing the style transfer on static images
    # You'll need a content.jpg and style.jpg in the same directory for this to run
    content_path = "content.jpg" # Example: a photo of yours
    style_path = "style.jpg"     # Example: Van Gogh's Starry Night

    # Create dummy images for testing if they don't exist
    try:
        Image.open(content_path)
    except FileNotFoundError:
        print(f"Creating dummy {content_path}")
        dummy_content = Image.new('RGB', (512, 512), color = 'red')
        dummy_content.save(content_path)
    try:
        Image.open(style_path)
    except FileNotFoundError:
        print(f"Creating dummy {style_path}")
        dummy_style = Image.new('RGB', (512, 512), color = 'blue')
        dummy_style.save(style_path)


    print("Starting style transfer...")
    stylizer = StyleTransfer(content_path, style_path, num_steps=200)
    output_image = stylizer.train()
    output_image.save("output.jpg")
    print("Style transfer complete. Output saved as output.jpg")

